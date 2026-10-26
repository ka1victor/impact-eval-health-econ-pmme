# Estrutura obrigatória da versão final da apresentação da banca 2

> **Decisão do autor, 26/10/2026.** Vale para toda versão futura do deck da banca
> 2. **Só a versão curta é usada.** As versões longas não serão usadas e não
> precisam mais ser geradas; o deck completo fica só como registro. Um deck que fuja desta estrutura
> está errado e deve ser corrigido no gerador
> (`scripts/apresentacao/gerar_deck_banca2.py`), não à mão.<br>
> **Estatuto:** regra de apresentação. Não muda protocolo nem resultado.

## 1. As seções, nesta ordem

| # | Seção | O que entra | O que não entra |
|---|---|---|---|
| 1 | **Hipótese** | **uma só** na versão final, depois que os professores validarem. Até lá pode haver mais de uma, mas as de plano B aparecem **em cinza**, visivelmente secundárias | várias hipóteses com o mesmo peso visual |
| 2 | **Dados** | variáveis principais e secundárias e a **fonte de cada uma** (base, órgão, período, unidade) | resultados |
| 3 | **Análise descritiva** | visão básica das variáveis importantes para o problema: tamanho das amostras, médias e distribuição das variáveis críticas (por exemplo, IVS × faixa, distribuição do IVS, vagas e preenchimento por ciclo) | estimativas causais |
| 4 | **Metodologia** | o método econométrico e a **especificação do nosso caso**: outcome, amostra, equação em palavras, o que é por ciclo, erro-padrão | premissas e testes de validade (vão para Identificação) |
| 5 | **Identificação** | as **premissas do método** e a **aderência do nosso caso** a cada uma: regra *sharp*, sem manipulação, continuidade, pacote do corte, tendências paralelas etc., cada uma com o teste ou argumento | resultados |
| 6 | **Resultados** | **gráficos da especificação principal** | especificações secundárias |
| 7 | **Robustez** | **gráficos das especificações secundárias**: controles a mais, outras janelas, outras medidas, placebos, IC honesto etc. | — |
| 8 | **Discussão** | **explicação simples em termos da teoria** (o modelo da banca 1: bolsa, custo do lugar, escolha, preenchimento) | jargão técnico novo |

## 2. Regras que continuam valendo

Todas as decisões anteriores do autor
([`05_discussao_historia_empirica.md`](05_discussao_historia_empirica.md), §1)
continuam, desde que caibam nesta estrutura:
- efeitos por corte, sem empilhado no corpo;
- pouco texto;
- figura grande com "Como ler";
- especificação em linguagem simples;
- números só de `output/`, com cautelas obrigatórias;
- **só o deck curto** (`output/apresentacao_banca2/deck_banca2_curto.pptx`
  e `.pdf`). O completo não é mais gerado nem atualizado.

## 3. Como o conteúdo atual se encaixa (proposta, a validar)

| Seção | Conteúdo que já existe |
|---|---|
| Hipótese | candidata a central: H3 (a bolsa pesa pouco perto da origem do médico, "incentivo limitado"). Em cinza, como plano B: H1 (preenchimento), H2 (escolha) e H4 (oferta). A escolha final é do autor, depois da validação dos professores |
| Dados | tabela de fontes; cronologia dos três ciclos; variáveis principais (faixa da bolsa, IVS 2010 oficial, vagas, alocados, escolhas, origem do candidato, horas no CNES) e secundárias (composição das vagas, concorrência, região, porte) |
| Análise descritiva | os três ciclos em números; IVS × faixa; distribuição do IVS; dados crus em volta dos cortes; 1ª opção em relação à origem; subida do preenchimento dentro das faixas (doc 57m) |
| Metodologia | slides de especificação de cada estimador |
| Identificação | premissas e testes (regra *sharp*, densidade, balanço, placebos, pacote do corte e auditorias 18 e 35, tendências paralelas) |
| Resultados | gráfico principal da hipótese central e de cada plano B |
| Robustez | antes e depois do controle; especificações do logit; TOST; Rambachan–Roth; diagnóstico da queda em 0,300 (doc 57l) |
| Discussão | incentivo limitado; por que a bolsa mexe na escolha e não no preenchimento; substituição na oferta |
