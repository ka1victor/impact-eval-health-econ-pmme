# S1b — Revisar o RDD da bolsa com o IVS administrativo (05/10/2026)

## Papel

Você é revisor independente dos commits `1faf0f4` e `be12956` do branch
`claude/compassionate-feynman-d70ipe`. Esse trabalho reverte uma conclusão
central do projeto (a de que a RDD da bolsa morreu no R1), então o ônus da
prova é dele. Revise **contra o repositório e contra as fontes oficiais**,
nunca contra a documentação que o próprio trabalho escreveu.

## Antes de começar

1. Leia `CLAUDE.md`, o plano
   [`14`](../../docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md), a
   auditoria [`15`](../../docs/auditorias/15_portao_r1_r2_ivs_administrativo.md)
   e o rascunho [`18`](../../docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md).
2. `git fetch origin claude/compassionate-feynman-d70ipe` e veja
   `git diff 127e3be..be12956`.
3. Monte o ambiente fixado (`uv venv --python 3.12 .venv && VIRTUAL_ENV=.venv uv pip install -r requirements.txt`)
   e rode `python run_tests.py`: o esperado são 203 testes verdes. Rode os
   conferidores `10_` e `11_`.

## O que revisar

### Fonte

1. Baixe de novo o quadro de vagas do PMMB 2026 pela URL do manifesto
   `output/aquisicao/a07_manifesto_ivs_administrativo.json` e compare o SHA-256
   com o registrado (`36f4ef26…`). Se o arquivo publicado mudou, registre; o R1
   usa a cópia preservada.
2. Abra a aba "Lista de Municípios-Tipo Equipe". Confirme que os rótulos de
   três colunas estão deslocados em relação aos dados (a coluna "Regiao" guarda
   o código IBGE) e que o script acha a chave pelo conteúdo, não pelo rótulo.
3. Confirme 5.571 municípios, um IVS por município e a categoria publicada
   igual aos cortes do Atlas aplicados ao IVS (5.571 de 5.571).

### R1

4. Reproduza **com código próprio, sem importar o `01c`**, as 4.103 de 4.103
   combinações município–onda–versão do quadro de vagas do PMM-E.
5. Confira que o mapeamento do FAQ de 2025 acerta só 202 dos 368 municípios de
   2025, ou seja, que a regra do edital de 2026 já era a aplicada em 2025.
6. Confira que nenhum município muda de faixa nos dez pares de ondas.
7. Confira a comparação com o IVS 2010: 38 valores idênticos, correlação 0,851
   e 2.999 municípios na mesma categoria.
8. Julgue se há motivo para achar que o IVS do quadro de 2026 difere do usado em
   julho de 2025. A reprodução de 100% em 2025 pesa contra; a safra continua
   não documentada. Diga se isso deveria bloquear o R3.

### R2

9. Confirme que nenhum outcome foi lido. Liste as entradas de `01c` e `04`. A
   série histórica entra só com código e rótulo; ela só tem linha para
   município com bolsista, e por isso serve de conferência, não de base.
10. Rode `04` duas vezes no ambiente fixado: as saídas têm de ser idênticas byte
    a byte.
11. **Ponto sensível — a ordem das decisões.** A regra estrita de
    randomização local foi a primeira a rodar e reprovou os dois cortes. A troca
    para local-linear com Holm veio depois, sem outcome, e a reprovação ficou
    registrada. Julgue:
    - se a troca é legítima;
    - se Holm a 5% é frouxo demais diante do limiar de 0,15 da regra estrita;
    - se a taxa de covariadas sinalizadas nos placebos `0,200` e `0,500` sustenta
      a leitura de acaso.
12. Confira a fórmula do MDE de desenho (variância sanduíche do salto
    local-linear sob variância constante) num exemplo pequeno feito à mão, e a
    combinação dos dois cortes por inverso da variância.
13. Confira as ressalvas: `capital` em `0,300`, IVS capital humano 2010 em
    `0,400` e a composição da oferta em `0,400` (p = 0,14).

### Documentação e pipeline

14. Notas datadas nos docs 14, 15 (pergunta), 16, 17 e no roadmap batem com os
    artefatos. O doc 07, gerado e não regerado, continua correto para o IVS
    2010.
15. As mudanças no gerador do red team (`07_red_team_sintese.py`) são só de
    estado: nenhuma cifra muda e os conferidores aprovam.
16. O controlador recusa protocolo R3 sem R1 e R2 aprovados, e resultado R4 sem
    registro R3. Teste numa cópia descartável do repositório, criando arquivos
    falsos, e nunca no repositório.
17. Os testes novos testam o que importa, e não só que o arquivo existe.

## O que entregar

Uma linha por commit:

| Commit | Veredito | Achados | Correção proposta |
|---|---|---|---|

O veredito é `APROVADO`, `APROVADO COM AJUSTE` ou `BLOQUEADO`. Para cada
achado, informe arquivo e linha, o que está errado, como verificou e a
gravidade.

Correção mecânica e sem decisão do autor vai em commit próprio. Se a correção
mudar número, protocolo ou leitura, **não corrija**: reporte. Não faça push nem
merge sem autorização do autor.
