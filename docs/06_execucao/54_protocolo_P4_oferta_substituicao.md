# 54. Protocolo P4: o programa cria oferta nova ou só passa a pagar quem já estava lá?

> **Data de congelamento:** 19/10/2026, antes de abrir o painel a16 por tempo de
> evento.<br>
> **Origem:** plano do doc 51 (P4, tarefas T4.1–T4.3), depois do portão G5
> (`docs/auditorias/aquisicao/A16_cnes_profissional.md`, `VIAVEL_PARCIAL`: a
> chave longitudinal é o código do profissional no CNES, não o CRM).<br>
> **Estatuto:** `EXPLORATORIO_P4`. A X1 já mostrou que 45–51% dos médicos tinham
> vínculo no município antes do início. Nada aqui tem fonte de exogeneidade
> validada. Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. Unidade, amostra e tempo

| Item | Definição |
|---|---|
| Unidade | médico do PMM-E ligado na X1 (regra D1 principal; literal como sensibilidade) × mês |
| Fonte | painel `output/aquisicao/cnes_profissional/` (202406–202608; nunca ≥ 202609) |
| Início | mês de `dt_inicio_atividade` da lista nominal (via X1) |
| Tempo de evento | e = mês − início |
| Janela principal | e ∈ [−6, +6] |
| Subamostra balanceada | médicos com todos os meses de −6 a +6 (início entre 202412 e 202602) |
| Janela longa | e ∈ [−12, +10], só onde houver cobertura, relatada com o n por e |

## 2. Outcomes por médico × mês

Horas semanais cadastradas:
- total;
- SUS;
- não SUS;
- ambulatorial e hospitalar.

Vínculos e locais:
- número de vínculos;
- número de estabelecimentos;
- número de municípios.

Onde estão as horas:
- no estabelecimento do posto PMM-E;
- no município do posto;
- fora dele.

Por tipo de estabelecimento:
- horas em estabelecimentos públicos (natureza jurídica da administração
  pública);
- horas em privados, com e sem fins lucrativos.

São horas **cadastradas**, não trabalhadas. Vínculo não é presença.

## 3. Especificações

| Id | Especificação | Leitura |
|---|---|---|
| T4.1a | médias por tempo de evento, na subamostra balanceada e na amostra completa, por ciclo | descritivo |
| T4.1b | evento escalonado no nível do médico: Callaway–Sant'Anna, coortes = mês de início, controles = médicos ainda não iniciados (início posterior, inclusive ciclo 3 até 202608), base g−1; agregação por e; teste conjunto dos pré; bootstrap multiplicador por médico (semente 20261019) | ATT de entrar no PMM-E sobre as horas do médico, sob tendências paralelas entre médicos que entram em datas diferentes; exploratório |
| T4.1c | T4.1b separado por origem: já tinha vínculo no município do posto antes do início (X1 b) ou não | incumbentes vs novos |
| T4.2 | para quem mudou de município, as horas que o médico deixou no município de origem; e a variação das horas de especialistas da mesma CBO no município de origem (painel CNES nacional) entre o pré e o pós | descritivo do deslocamento |
| T4.3 | contabilidade líquida: Δ horas no município do posto − Δ horas fora dele, somadas por curso e por estrato de IVS (só para tabular, sem contraste no corte) | descritivo |

Os estratos de IVS no T4.3 são só de tabulação, pelas faixas da bolsa. Não há
RDD aqui.

## 4. Relato

- Todas as linhas são relatadas.
- BKY dentro do T4.1b e do T4.1c.
- Figuras com "Como ler".
- Linguagem: "associado à entrada", "horas cadastradas".
- O efeito de entrar no programa não é o efeito da bolsa nem do PMM-E sobre o
  município.

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/28_trajetoria_medicos.py` |
| estimativas | `output/rdd_bolsa/P4_estimativas.csv` |
| resumo | `P4_resumo.json` |
| figuras | `P4_figuras/` |
| resultados | `docs/06_execucao/57d_resultados_P4_trajetoria.md` |

## 6. Integridade

- Nada imputado.
- Mês sem o médico no CNES é "sem vínculo cadastrado", relatado à parte. Não
  vira zero de horas se o mês inteiro falta na fonte; se o médico só não
  aparece, conta como zero vínculos, com rótulo.
- Sem nome, CPF, CNS ou CRM em `output/`.
- O arquivo de IVS errado não é lido.
- Nenhum mês ≥ 202609.
