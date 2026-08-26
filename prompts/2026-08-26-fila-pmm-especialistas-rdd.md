# Fila Mais Médicos Especialistas (PMM-E) — RDD nos Cortes de IVS 2010 (0,300 e 0,400)

> Escrito em 26/08/2026. Pré-requisito: nenhum (dados 100% públicos e abertos, sem necessidade de LAI).
> Documentos de contexto: `02-saude/69-auditoria-cinco-propostas-distancia.md` (§69.2),
> `02-saude/66-agora-tem-especialistas-e-a-familia.md` e `tools/geo8_pmm_especialistas_rdd.py`.
>
> **Critério de parada (Kill Criterion):** Parada imediata e encerramento do tema se o primeiro estágio
> ($\tau_1$ ou $\tau_2$) sobre taxa de preenchimento de vagas imediatas ou horas no CNES não apresentar
> salto estatisticamente significativo ao nível de 5% ou mudar de sinal nas janelas de sensibilidade
> ($h \in [0{,}015; 0{,}030]$).

```
Repositório de validação de temas de pesquisa empírica. Leia o CLAUDE.md e o AGENTS.md
primeiro, e obedeça as cinco regras, a sexta (objeção só vale se virar estatística com
limiar) e as convenções de escrita: português do Brasil, mensagem de commit sem acento,
comentário de código sem acento, travessão com parcimônia.

OBJETIVO DA SESSÃO: Executar a auditoria de primeiro estágio e identificação causal para o líder
de política pública de economia da saúde e trabalho médico: Mais Médicos Especialistas (PMM-E 2025/2026).

MOTIVAÇÃO DE POLÍTICA PÚBLICA (Formato obrigatório de 4 propriedades do AGENTS.md):
1. Quem usa o número e para quê: SGTES/MS e CONASS, para calibrar os valores de bolsa do Programa
   "Agora Tem Especialistas", definindo o piso de incentivo necessário para fixar profissionais no interior.
2. Converte o achado em decisão, não em adjetivo: Quantifica a elasticidade-salário de atração médica e o
   trade-off entre subsidiar a fixação local vs. custear o transporte sanitário até polos regionais.
3. Predição com direção e data: A descontinuidade salarial de +50% (R$ 15k vs R$ 10k) e +33% (R$ 20k vs R$ 15k)
   produz salto discreto no preenchimento de vagas e redução no bypass de pacientes no SIA em 2026.
4. Declara o limite do que o número sustenta: Identifica a resposta de curto prazo da oferta de especialistas
   e volume de consultas locais no SIA; não sustenta desfechos de mortalidade agregada no 1º ano.

COMO TRABALHAR:
Subagentes ou execução sequencial. Downloads de dados públicos apenas para pastas estruturadas em output/
ou output/bases_saude_externas/. Relatórios gravados em notas em 02-saude/.

A FILA DE TAREFAS:

P1. COMPILAÇÃO DA BASE MUNICIPAL DE IVS E VAGAS DOS CHAMAMENTOS (SGTES/MS)
    a) Obter o IVS 2010 (Índice de Vulnerabilidade Social do IPEA) para os 5.570 municípios brasileiros;
    b) Tabular as vagas ofertadas nos Editais dos Chamamentos Públicos SGTES/MS nº 3/2025 e nº 6/2026
       por município, UF, especialidade médica (CBO) e pontuação de corte;
    c) Classificar cada município nas 3 faixas de bolsa:
       - Faixa 3 (IVS <= 0,300): R$ 10.000,00/mês
       - Faixa 2 (0,300 < IVS <= 0,400): R$ 15.000,00/mês (+50%)
       - Faixa 1 (IVS > 0,400): R$ 20.000,00/mês (+33,3%)
    d) Mapear a contagem de municípios e vagas nas janelas h in [0,015; 0,030] em torno de c1=0,300 e c2=0,400.

P2. AUDITORIA DE PRIMEIRO ESTÁGIO NO CNES E DADOS ABERTOS DO MAIS MÉDICOS
    a) Baixar dados abertos de profissionais ativos do Provimento Federal (dadosabertos.saude.gov.br);
    b) Cruzar com os microdados mensais do CNES (tbCargaHorariaSus e tbAtividadeProfissional);
    c) Construir os 4 desfechos de primeiro estágio por município-especialidade:
       1. Taxa de preenchimento da vaga no 1º chamamento (0/1);
       2. Entrada efetiva do médico em exercício (0/1);
       3. Retenção aos 6 e 12 meses (meses ativos);
       4. Carga horária médica especializada municipal (FTE por 1.000 hab).

P3. ESTIMAÇÃO ECONOMÉTRICA DE RDD E RANDOMIZAÇÃO LOCAL
    a) Estimar o modelo de descontinuidade em dois cortes:
       Y_{m,s} = alpha + tau_1 * 1(IVS_m > 0,300) + tau_2 * 1(IVS_m > 0,400) + f(IVS_m) + gamma_s + eps_{m,s}
    b) Executar inferência por randomização local (testes de permutação exata) com cluster no município;
    c) Testar sensibilidade à largura de banda (h in [0,015; 0,030]) e testar placebos em falsos cortes
       (ex.: IVS = 0,250 e IVS = 0,350);
    d) Avaliar o Kill Criterion: se tau_1 ou tau_2 não tiverem p < 0,05 ou trocarem de sinal, declarar parada.

P4. DESFECHOS AMBULATORIAIS E TAXA DE BYPASS NO SIA
    a) Se aprovado no P3, cruzar com a produção ambulatorial do SIA (BPA-I e APAC) por especialidade;
    b) Estimar o impacto sobre:
       1. Volume de consultas ambulatoriais locais por 1.000 hab;
       2. Taxa de evasão/bypass (% de residentes que viajam para polos regionais para a mesma especialidade);
    c) Calcular a elasticidade-salário de fixação médica e comparar com o custo de transporte intermunicipal.
```
