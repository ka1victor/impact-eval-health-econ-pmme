# Fila PMM-E: Decomposição de Resolutividade Local vs. Resolutividade Global no SIA/SIH

> Escrito em 26/08/2026. Pré-requisito: `tools/geo8_pmm_analise_completa.py` e nota `02-saude/70-mais-medicos-especialistas-rdd-ivs.md`.
> Documentos de contexto: `02-saude/66-agora-tem-especialistas-e-a-familia.md` e `02-saude/68-a-margem-que-nao-se-ve-e-o-par-do-tiss.md`.
>
> **Critério de Parada (Kill Criterion):** Parada imediata e descarte da hipótese de expansão de demanda reprimida
> se o salto causal em Resolutividade Global ($\tau_{R\_global}$) for estatisticamente indistinguível de zero ($p > 0{,}10$)
> em todas as janelas $h \in [0{,}015; 0{,}030]$ no corte $c_1 = 0{,}300$, reduzindo a política a substituição puramente geográfica.

```
Repositório de validação de temas de pesquisa empírica. Leia o CLAUDE.md e o AGENTS.md
primeiro, e obedeça as cinco regras, a sexta (objeção só vale se virar estatística com
limiar) e as convenções de escrita: português do Brasil, mensagem de commit sem acento,
comentário de código sem acento, travessão com parcimônia.

OBJETIVO DA SESSÃO: Decompor o impacto causal do Programa Mais Médicos Especialistas (PMM-E)
em duas margens econômicas fundamentais:
1. Margem de Substituição Geográfica (Resolutividade Local): Retenção de pacientes no próprio município;
2. Margem de Expansão do Cuidado (Resolutividade Global): Destravamento de demanda reprimida e aumento
   líquido na taxa de diagnósticos e consultas per capita da coorte de residentes.

MOTIVAÇÃO DE POLÍTICA PÚBLICA (Formato obrigatório de 4 propriedades do AGENTS.md):
1. Quem usa o número e para quê: SGTES/MS, Secretaria de Atenção Especializada (SAES/MS) e CONASS,
   para avaliar se o provimento de especialistas no interior apenas transfere o faturamento da capital
   para o município polo ou se efetivamente expande a cobertura diagnóstica de pacientes desassistidos.
2. Converte o achado em decisão, não em adjetivo: Distingue se a alavanca de política gera benefício
   por redução de custo logístico (substituição) ou por ganho clínico de diagnósticos adicionais (expansão),
   calibrando a meta de expansão de vagas entre atenção ambulatorial e rede hospitalar.
3. Predição com direção e data: No corte c1 = 0,300 (salto de bolsa de R$ 10k para R$ 15k), a taxa de
   resolutividade local salta em +34 p.p. e a taxa de exames diagnósticos globais por 1.000 hab cresce
   líquido em pelo menos +15% a partir do 2º semestre de 2026.
4. Declara o limite do que o número sustenta: Identifica a expansão de consultas e exames diagnósticos
   ambulatoriais (SIA) e cirurgias eletivas (SIH); não sustenta redução de mortalidade geral em 12 meses.

COMO TRABALHAR:
Subagentes ou execução sequencial. Downloads de microdados para pastas estruturadas em output/.
Relatório consolidado gravado em nova seção ou nota dedicada em 02-saude/.

A FILA DE TAREFAS:

P1. EXTRAÇÃO E ESTRUTURAÇÃO DO FLUXO AMBULATORIAL NO SIA (2024-2026)
    a) Filtrar os microdados do SIA-PA por pares de município de residência (origem) e município
       de atendimento (destino), identificando:
       - Q_local(m, t, s): Produção realizada no próprio município m para residentes de m;
       - Q_externo(m, t, s): Produção realizada fora de m para residentes de m;
       - Q_global(m, t, s) = Q_local(m, t, s) + Q_externo(m, t, s): Cuidado total recebido pelos residentes.
    b) Desagregar por 5 domínios clínicos dos editais:
       1. Saúde da Mulher / Câncer de Colo e Mama (Colposcopia, Mamografia, USG);
       2. Saúde Digestiva / Câncer Colorretal e Gástrico (Colonoscopia, Endoscopia);
       3. Cardiologia e Risco Cirúrgico (Ecocardiografia);
       4. Cirurgia Geral e Procedimentos Ambulatoriais Resolutivos;
       5. Otorrinolaringologia (Videolaringoscopia).

P2. CONSTRUÇÃO DAS MÉTRICAS DE RESOLUTIVIDADE LOCAL E GLOBAL
    a) Métrica 1 - Resolutividade Local (% retido):
       R_local(m, s) = Q_local(m, s) / max(1, Q_global(m, s))
    b) Métrica 2 - Taxa de Resolutividade / Acesso Global (por 1.000 hab):
       R_global(m, s) = (Q_global(m, s) / População(m)) * 1.000
    c) Métrica 3 - Decomposição de Margens (Substituição vs. Expansão):
       - Delta Q_local (Margem Local);
       - Delta Q_externo (Margem de Bypass / Deslocamento);
       - Delta Q_global (Margem Extensiva / Demanda Reprimida Destravada).

P3. RESOLUTIVIDADE CIRÚRGICA E HOSPITALAR NO SIH
    a) Mapear internações cirúrgicas de residentes de m no SIH (AIH):
       - Cirurgias eletivas realizadas no hospital municipal (CAR_INT = 01);
       - Internações cirúrgicas de urgência e transferências para hospitais polos (CAR_INT = 02);
    b) Construir a Taxa de Resolutividade Cirúrgica Local:
       R_cirurgica(m) = Cirurgias Eletivas Locais / (Cirurgias Eletivas Locais + Urgências Transferidas).

P4. ESTIMAÇÃO ECONOMÉTRICA RDD E TESTES DE HIPÓTESES
    a) Estimar o RDD nos cortes de IVS 2010 (c1 = 0,300 e c2 = 0,400) para cada desfecho:
       Y_{m,s} = alpha + tau_1 * 1(IVS_m > 0,300) + tau_2 * 1(IVS_m > 0,400) + f(IVS_m) + gamma_s + eps_{m,s}
    b) Executar inferência por randomização local (testes exatos de permutação de Fisher-Pitman com 2.000 replicações);
    c) Testar sensibilidade à largura de banda (h in [0,015; 0,030]);
    d) Testar placebos em falsos cortes (IVS = 0,250 e IVS = 0,350);
    e) Construir o Índice Padronizado de Resolutividade Global (Kling, Liebman & Katz, 2007) e FDR de Anderson;
    f) Avaliar o Kill Criterion: verificar se tau_{R_global} > 0 com p < 0,10.

P5. SÍNTESE E ANÁLISE CUSTO-BENEFÍCIO AMPLIADA
    a) Calcular o valor econômico do destravamento de demanda reprimida (anos de vida ajustados / QALYs implícitos
       por diagnóstico precoce);
    b) Consolidar tabelas em CSV/JSON em output/ e documentar na nota correspondente em 02-saude/.
```
