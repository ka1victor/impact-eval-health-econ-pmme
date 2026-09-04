# Suíte de Testes Automatizados do PMM-E

Este diretório reúne a suíte de testes automatizados do projeto, composta por **102 testes em 13 módulos**, garantindo a integridade substantiva, metodológica, computacional e documental da pesquisa.

---

## 1. Como Executar os Testes

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
| [`test_provimento_cnes_a5.py`](test_provimento_cnes_a5.py) | A5 Dinâmica CNES | Avaliação da oferta médica local cadastrada no CNES (amostra confirmatória de 587 células em 295 municípios, referência 202506 e follow-up 202603, tom estritamente associativo). |
| [`test_red_team_a6.py`](test_red_team_a6.py) | A6 Red Team | Auditoria das 11 afirmações substantivas na matriz afirmação–evidência–limite e validação do manifesto de hashes reproduzíveis. |
| [`test_tipologia_territorial.py`](test_tipologia_territorial.py) | A2 Território | Classificação em 4 estratos (Capital, Metropolitano, Interior Próximo e Interior Remoto) via REGIC 2018 + RM/RIDE 2022 strict, sem consulta a desfechos. |
| [`test_reconciliacao_funil_ciclo1.py`](test_reconciliacao_funil_ciclo1.py) | A1 Funil | Auditoria de confirmações em células de reserva e formalização do portão `APROVADO_CELULA`. |
| [`test_pre_analise_atracao.py`](test_pre_analise_atracao.py) | A3 Pré-Análise | Congelamento dos contrastes e MDEs calculados antes da estimação de A4, verificação de hashes de entrada e clusterização. |
| [`test_tema_atracao_provimento.py`](test_tema_atracao_provimento.py) | Auditoria de Tema | Viabilidade do tema de atração administrativa e delimitação entre provimento local e retenção individual. |
| [`test_viabilidade_salario_ivs.py`](test_viabilidade_salario_ivs.py) | RDD Bolsa | Verificação da falha de replicação das faixas salariais em 177 municípios e encerramento preventivo do portão R1 do RDD. |
| [`test_coorte_c3.py`](test_coorte_c3.py) | Ciclo 3 Coorte | Congelamento dos cursos 1, 12 e 24 com suporte integral e verificação da assinatura cadastral (Nota Técnica nº 59/2026). |
| [`test_sih_pre_c3.py`](test_sih_pre_c3.py) | Ciclo 3 SIH Pré | Auditoria dos dados hospitalares do SIH, dicionário SIGTAP e regra *fail-closed* ante ausência de arquivos no FTP. |
| [`test_pre_analysis_c3.py`](test_pre_analysis_c3.py) | Ciclo 3 Pré-Análise | Torneio pré-tratamento de anestesiologia e congelamento de protocolo antes da maturidade de 202703. |
| [`test_datasus_parser.py`](test_datasus_parser.py) | Utilitário DBC | Validação funcional da rotina de descompressão e conversão de arquivos `.dbc` do DATASUS. |

---

## 3. Padrões de Teste

1. **Isolamento e determinismo:** Os testes operam sobre os artefatos congelados em `output/` e garantem que qualquer alteração de código que degrade coeficientes, altere amostras ou quebre links da documentação seja imediatamente detectada.
2. **Sem dados sintéticos desavisados:** Nenhum teste deve aceitar dados simulados como se fossem bases reais.
3. **Auditoria de Documentação:** Testes verificam automaticamente a consistência entre o texto publicado e as tabelas numéricas salvas.
