# A17 — SIA/SUS no TabNet por município × mês × forma de organização × curso (adendo §12.2 do protocolo 47)

> **Data:** 19/10/2026.<br>
> **Tarefa:** aquisição do adendo §12.2 do protocolo
> [`06_execucao/47`](../../06_execucao/47_protocolo_producao_especializada.md)
> (T3.2 do plano [`51`](../../06_execucao/51_plano_perguntas_reformuladas.md)):
> produção ambulatorial por forma de organização, filtrada pelas CBO de cada curso
> da classe "específico" do portão [G4](../G4_viabilidade_especialidade.md).<br>
> **Script:** [`scripts/aquisicao/a17_adquirir_sia_forma_curso.py`](../../../scripts/aquisicao/a17_adquirir_sia_forma_curso.py).<br>
> **Números:** no resumo gerado,
> [`output/aquisicao/sia_forma_curso/a17_resumo.md`](../../../output/aquisicao/sia_forma_curso/a17_resumo.md),
> e no manifesto
> [`manifesto_sia_forma_curso.json`](../../../output/aquisicao/sia_forma_curso/manifesto_sia_forma_curso.json).
> As listas marcadas abaixo são conferidas contra o manifesto por
> `tests/test_aquisicao_sia_forma_curso.py`.<br>
> **Cegamento:** só aquisição. Nada foi calculado por IVS, faixa da bolsa, lado de
> corte, tratamento ou chegada; o script não lê IVS. O outcome do §12.2 (formas
> típicas por 10 mil habitantes) não foi montado aqui. Natureza dos dados: `EMPIRICO`.

## 1. Resultado

O painel cobre os 55 meses de processamento de 202201 a 202607, os 5.571
municípios do formulário do TabNet e os oito cursos "específico" do G4. Todas as
validações obrigatórias passaram. As 564 consultas responderam na primeira
tentativa (19/10/2026, 21h15–22h07 UTC). Nenhum mês ≥ 202609 foi pedido.

Cursos e conjuntos de CBO:
<!-- a17_conjuntos -->
- c07: curso 7 (CBO 225165, 225280, 225310)
- c10_c11: cursos 10 e 11 (CBO 225165, 225310)
- c12: curso 12 (CBO 225121)
- c13: curso 13 (CBO 225330)
- c14: curso 14 (CBO 225255, 225320)
- c15: curso 15 (CBO 225275)
- c16: curso 16 (CBO 225148, 225305, 225325)
<!-- /a17_conjuntos -->

Os cursos 10 e 11 têm as mesmas CBO e compartilham a consulta; o painel repete as
linhas para os dois. As CBO do curso 10/11 estão contidas nas do curso 7.

**Uma forma fica fora da dimensão.** Com Coluna = Forma organização, o TabNet
descarta os registros cuja forma não está na sua tabela de formas. Nas CBO
destes cursos isso acontece com um só procedimento, a partir de 202501:
<!-- a17_procedimentos_fora -->
0301160015
<!-- /a17_procedimentos_fora -->

É a "reabilitação em falência intestinal em nível ambulatorial", da forma 030116,
que não aparece na lista de formas do formulário. São 984 procedimentos aprovados
em 19 meses, contra cerca de 499 milhões das CBO dos cursos em 202201–202607. Essa
produção não está no painel nem em nenhum Total por forma: não é zero nem
ausente, fica fora da dimensão. A quantidade, mês a mês, está em
`sia_forma_curso_procedimentos_fora_da_coluna_forma.csv`.

**Cruzamento com o a12.** Somadas por subgrupo, as formas reproduzem a tabela
nacional CBO × subgrupo do a12 em 347 dos 385 pares mês × conjunto. Os 38 pares
restantes são os conjuntos c07 e c10_c11 de 202501 a 202607, só no subgrupo
0301. Neles o a17 tem menos que o a12, e a falta cabe toda no procedimento acima
(nenhuma diferença sem explicação). Nos meses 202509–202607 o a12 foi conferido
também contra a safra v2 do a12b, que é igual à v1
([A12b/A13b](A12b_A13b_safras_v2.md)).

**Formas típicas do G4.** Todas as 25 formas típicas dos oito cursos são coluna
da resposta nos 55 meses.

## 2. Fonte e consultas

- **Formulário:** o do a12,
  `http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qabr.def`, "Produção
  Ambulatorial do SUS - Brasil - por local de atendimento". Só HTTP.
- **Código importado, não redigitado:** o script carrega uma instância própria do
  a12 e usa dela o formulário, a lista de municípios, as opções de CBO, o POST, o
  cache com SHA-256, as tentativas com espera crescente, o leitor `prn`, o eco de
  período e filtros, a separação de "município ignorado" e a regra de sinal de
  queda. Só o diretório de cache e o padrão de coluna (forma, 6 dígitos, em vez de
  subgrupo, 4 dígitos) mudam, e só nessa instância.
- **Cursos:** classe `ESPECIFICO` de `output/rdd_bolsa/G4_resumo.json`. As CBO
  vêm da ponte curso–CBO pela função `carregar_ponte` do script do G4 e têm de
  coincidir com as do G4.

| Consulta | Linha | Coluna | Filtro de CBO | Por mês | Uso |
|---|---|---|---|---|---|
| `municipio_forma_<conjunto>` | Município | Forma organização | CBO do conjunto | 7 | painel (`exibirlz`) |
| `cbo_forma_uniao` | Profissional - CBO | Forma organização | união das 11 CBO | 1 | total nacional por forma de cada conjunto (V3) |
| `conferencia_forma_<UF>_<conjunto>` | Município | Forma organização | CBO do conjunto + UF | 14 em 202506 | AC e RR célula a célula (V4) |
| `diag_procedimento_sem_coluna`, `diag_procedimento_forma` | Procedimento | Não ativa; Forma organização | união das 11 CBO | 2 | procedimentos fora da coluna de forma (V8) |

São 55 × 8 + 14 + 55 × 2 = 564 POSTs, sequenciais, com 1,5 s de pausa. Para cada
um, o manifesto guarda URL, corpo, data e hora, SHA-256 e tamanho da resposta.

As consultas de diagnóstico (V8) foram acrescentadas depois de ver a V5. Elas só
explicam a diferença frente ao a12; não mudam o painel.

## 3. Tempo, lugar e unidade

- **Tempo:** mês de processamento (arquivo `qabrAAMM.dbf`), não de atendimento.
- **Lugar:** município do estabelecimento (local de atendimento), não de
  residência.
- **Unidade:** município × mês × forma de organização × curso. Quantidade
  aprovada (`Qtd.aprovada`) de procedimentos ambulatoriais pelo SUS.

| Coluna | Definição |
|---|---|
| `co_ibge` | município de atendimento, 6 dígitos do TabNet |
| `competencia_processamento` | `AAAAMM` |
| `cod_curso` | curso do PMM-E (código da ponte) |
| `forma` | forma de organização SIGTAP, 6 dígitos |
| `qtd_aprovada` | inteiro; nulo só quando o município falta na resposta |
| `status` | `valor_tabnet`, `zero_tabnet` ou `municipio_ausente_da_resposta` |
| `natureza_dos_dados` | sempre `EMPIRICO` |

## 4. Zeros e ausências (regras do a12)

- `-` do TabNet é zero (legenda da página): `qtd_aprovada = 0`, `status =
  zero_tabnet`.
- Município do formulário que não vem na resposta: `qtd_aprovada` nula, `status =
  municipio_ausente_da_resposta`. Não aconteceu nesta extração.
- Forma que não é coluna da resposta não gera linha: o TabNet omite colunas sem
  registro sob o filtro. A presença de cada forma em cada consulta está em
  `sia_forma_curso_formas_por_consulta.csv`; a V3 confere que a soma das CBO do
  conjunto é zero nessas formas.
- Consulta que falha não gera linha; a consolidação para.
- "Município ignorado" fica em `sia_forma_curso_ignorados.parquet`, nunca num
  município.

## 5. Validações

| Id | Validação | Tipo |
|---|---|---|
| V1 | em cada resposta, linha Total = soma das linhas e coluna Total = soma das células | obrigatória |
| V2 | conjunto contido noutro (c10_c11 em c07) tem quantidade ≤ em cada célula município × forma × mês | obrigatória |
| V3 | total nacional de cada conjunto por forma = soma das suas CBO na consulta por CBO; forma ausente da municipal tem soma zero | obrigatória |
| V4 | AC e RR em 202506, cada conjunto: célula a célula igual à consulta nacional | obrigatória |
| V5 | soma das formas por subgrupo contra a tabela nacional CBO × subgrupo do a12 (v1; e v2 em 202509–202607) | relato |
| V6 | cobertura por mês e conjunto (limiares do a12) e presença das formas típicas do G4 | relato |
| V7 | eco de período e filtros; nenhum mês ≥ 202609 | obrigatória |
| V8 | procedimentos que somem com Coluna = Forma; coerência interna (totais por forma = consulta por CBO; diferença dos Totais = soma dos que somem) obrigatória | relato |

Por que o total nacional por forma é conferido contra a consulta por CBO, e não
contra uma consulta por UF de cada conjunto: a consulta Linha = CBO × Coluna =
Forma é independente da municipal e confere cada forma de cada conjunto com uma
só consulta por mês. A conferência por UF fica na V4, célula a célula.

A V6 sinaliza vários meses de 2022 (produção abaixo da mediana do conjunto). É só
relato; nada foi corrigido.

## 6. Limites

- **A CBO é mais larga que o curso** (G4 §3). O painel mede a produção das CBO do
  curso, não o conteúdo do curso. O curso 14 herda toda a radiologia da CBO
  225320; os cursos 10 e 11 não se distinguem.
- Só produção ambulatorial do SUS (SIA). Cirurgias em AIH não têm CBO no TabNet.
- Procedimento cuja forma não está na tabela do TabNet fica fora (seção 1). Uma
  forma nova pode entrar nessa situação em meses futuros; a V8 mostra isso.
- CBO informada pelo prestador; produção sem CBO na tabela não entra.
- Mês de processamento: reapresentações caem no mês em que são processadas. Os
  meses recentes podem ser revistos pela fonte (A15 §5); nesta extração o SIA
  dos meses 202509–202607 não foi revisto.

## 7. Saídas

| Arquivo | Conteúdo |
|---|---|
| `painel_sia_municipio_mes_forma_curso.parquet` | painel longo, denso nas formas que são coluna da resposta |
| `sia_forma_curso_ignorados.parquet` | "município ignorado" e exterior, por conjunto |
| `sia_forma_curso_nacional_cbo_forma.parquet` | CBO × forma × mês, nacional (consulta da V3) |
| `sia_forma_curso_formas_por_consulta.csv` | presença de cada forma em cada consulta e totais da V3 |
| `sia_forma_curso_cobertura_mes.csv` | cobertura por mês e conjunto, com o sinal da V6 |
| `sia_forma_curso_cruzamento_a12.csv` | V5 por mês × conjunto × subgrupo |
| `sia_forma_curso_cursos.csv` | cursos, CBO, conjunto e rótulos do TabNet |
| `sia_forma_curso_formas_tipicas.csv` | formas típicas do G4: meses presentes e quantidade nacional |
| `sia_forma_curso_procedimentos_fora_da_coluna_forma.csv` | V8 por mês e procedimento |
| `manifesto_sia_forma_curso.json`, `a17_resumo.md` | proveniência, validações e resumo gerado |
| `brutos/` | respostas brutas (gzip) e metadados; fora do controle de versão |

## 8. Reprodução

```bash
python3 scripts/aquisicao/a17_adquirir_sia_forma_curso.py                     # verificar (sem rede, não grava)
python3 scripts/aquisicao/a17_adquirir_sia_forma_curso.py --etapa tudo        # baixa para o cache e consolida
python3 scripts/aquisicao/a17_adquirir_sia_forma_curso.py --etapa consolidar  # só refaz as saídas do cache
python3 -m pytest tests/test_aquisicao_sia_forma_curso.py
```

O `run_all.py` roda o a17 em `--etapa verificar`, depois do a12b (cuja tabela CBO
× subgrupo a V5 lê). O cache bruto fica fora do controle de versão. Uma nova
extração pode não reproduzir os SHA-256 dos meses recentes.
