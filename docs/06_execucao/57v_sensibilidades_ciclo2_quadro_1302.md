# 57v. Sensibilidades da escolha no ciclo 2 com o tipo de vaga do quadro de 13/02/2026 (adendo 52d)

> **Gerado por** `scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py` a partir de `output/rdd_bolsa/VD_*`; não editar à mão (o teste `tests/test_sensibilidades_ciclo2_quadro_1302.py` confere que este arquivo é igual ao gerado; `--atualizar-doc` o regrava das saídas).<br>
> **Adendo:** [`52d_adendo_sensibilidades_ciclo2_quadro_1302.md`](52d_adendo_sensibilidades_ciclo2_quadro_1302.md), congelado em 26/10/2026 antes de rodar (commit `c87ed75`); SHA-256 em `adendo` de `VD_resumo.json`, conferido pelo teste. Protocolos de origem: [40](40_protocolo_multioutcome_rdd_bolsa.md) (E9, §12), [52](52_protocolo_P1_escolha_dap.md) (P1) e [52b](52b_protocolo_P1h_magnitudes.md) (P1h); adendo [52c](52c_adendo_vaga_imediata_ciclo2.md) (principais corrigidas, doc [57p](57p_escolha_vaga_imediata_c2.md)).<br>
> **Estatuto:** `ADENDO_52D_POS_RESULTADO`. As versões com o quadro de 19/03 (docs 42, 57a e 57i) e as principais corrigidas do adendo 52c (doc 57p) já tinham sido vistas; isto não é teste confirmatório novo. Toda linha de `VD_estimativas.csv` e o resumo têm `natureza_dos_dados = EMPIRICO`.<br>
> **Motivo:** [auditoria 41](../auditorias/41_auditoria_escolha_vaga_imediata_c2.md), achado A1: as sensibilidades que sustentam a robustez do ciclo 2 ([doc 44](44_sintese_rdd_bolsa_multioutcome.md)) ainda usavam o tipo de vaga do quadro retificado de 19/03/2026, refeito depois do resultado preliminar ([auditoria 36](../auditorias/36_auditoria_dados_H1.md)).<br>
> **Saídas:** `output/rdd_bolsa/VD_estimativas.csv`, `VD_resumo.json` e `VD_figuras/VD_antigo_corrigido.png`. As saídas `E9_*`, `P1_*`, `P1h_*` e `VC_*` não são regravadas, e os docs 42, 44, 57, 57a, 57i e 57p não são editados.<br>
> **Auditoria:** pendente.

## 1. Resposta curta

*Pendente: preenchido pelo script depois do portão de reprodução.*

## 2. Portão de reprodução (VD-5)

*Pendente: preenchido pelo script depois do portão de reprodução.*

## 3. O que usa o tipo de vaga do ciclo 2

<!-- VD:inventario:inicio -->
Lido do código dos scripts 16, 25 e 25c, antes de qualquer estimativa. "Usa" quer dizer que a linha depende de `tem_vaga_imediata`, `log_vagas_imediatas_mais_1` ou da definição do conjunto "só células com vaga imediata" no ciclo 2. As linhas que não usam não precisam ser refeitas e não são.

| Linha (origem) | Usa o tipo de vaga do ciclo 2? | Por onde | Neste adendo |
|---|---|---|---|
| E9, conjunto "só células com vaga imediata", ciclo 2 e empilhado (doc 42) | sim | define o conjunto e os candidatos; `log_vagas_imediatas_mais_1` é covariável (`tem_vaga_imediata` é constante e sai) | refeita (VD-1, VD-2) |
| E9, mesmo conjunto, ciclos 1 e 3 | não | o tipo de vaga só muda no ciclo 2 | não refeita |
| P1 M2 (log da distância) | sim | `tem_vaga_imediata` e `log_vagas_imediatas_mais_1` do M1, ciclos 1–3 empilhados | refeita (VD-3) |
| P1 M4 (efeito fixo de UF da vaga) | sim | idem | refeita (VD-3) |
| P1 M6 da nota, do município e do curso | sim | idem, mais as interações da bolsa | refeitas (VD-3) |
| P1 M7 (logit explodido) | sim | idem, nos postos 1 e 2 | refeita (VD-3) |
| P1 M8 (logit misto) | sim | matriz do M1 e partida no M1 | refeita (VD-3) |
| P1 M9 (logit aninhado) | sim | matriz do M1 e partida no M1 | refeita (VD-3) |
| P1 M3 (origem mais próxima) | — | não foi estimado no P1 (`NAO_EXECUTADO`) | nada a refazer |
| DAP do M1, quatro atributos, delta e bootstrap (doc 57a) | sim | β e atributos do M1; "1 vaga imediata" é a própria covariável | refeita (VD-4) |
| DAP do M4 e do M7 | sim | coeficientes do M4 e do M7 | refeitas (VD-4) |
| DAP do M5, ciclo 2 | sim | coeficientes do M5 do ciclo 2 | refeita (VD-4) |
| DAP do M5, ciclos 1 e 3 | não | ciclos sem mudança | não refeitas |
| km equivalentes K5 e K10 (P1h-2, M1; doc 57i) | sim | β e distância do M1 | refeitas (VD-4) |
| D_UF do P1h-3 no M2, no M4 e no M7 | sim | coeficientes dessas variantes | refeitas (VD-4) |
| D_UF do P1h-3 no M5 | ciclo 2 sim; ciclos 1 e 3 não | coeficientes do M5 de cada ciclo | recalculadas só para o BKY da família (o ciclo 2 já estava no 52c) |

Fora do §1 do adendo também usam o tipo de vaga do ciclo 2, e não são refeitas aqui: o logit explodido e as variantes quadrática e de degraus do E9 no conjunto principal; o M0 do P1; a ponte P1g (salto previsto pelo M1); os pesos descritivos da figura do P1h. Fica registrado para o autor.
<!-- VD:inventario:fim -->

## 4. Resultados

*Pendente: preenchido pelo script depois do portão de reprodução.*

## 7. Decisões de implementação

<!-- VD:decisoes:inicio -->
Decisões de implementação onde o adendo não fixava o detalhe. Foram registradas e commitadas antes de qualquer estimativa deste adendo (o histórico do Git mostra o commit do bloco antes do commit dos números). Nenhuma muda a amostra, o conjunto de escolha principal ou a especificação dos modelos de origem.

1. **Conjunto "só células com vaga imediata" com o quadro de 13/02** (26/10/2026). O §2 manda tirar do quadro de 13/02 a definição do conjunto de escolha "só células com vaga imediata", sem dizer como. *Resolução:* Mesma regra do script 12 (`conjunto_escolha` e `tabela_escolhas`): o conjunto é o subconjunto `tem_vaga_imediata == 1` do conjunto principal, e entram os candidatos com `celula_com_vaga_imediata == 1` (1ª opção em célula com vagas imediatas > 0). No ciclo 2, a regra é aplicada ao conjunto principal corrigido pela função `corrigir` do script 42 e à marca da 1ª opção refeita com as vagas imediatas de 13/02. Antes, o script confere que a mesma regra, aplicada ao quadro de 19/03, reproduz célula a célula o conjunto gravado pelo script 12 e a marca gravada de cada candidato; se não reproduzir, para. Célula escolhida sem linha ou sem número no quadro de 13/02 faz parar: nada é imputado.
2. **Especificação do E9 no VD-1 e no VD-2** (26/10/2026). No conjunto de sensibilidade, o doc 42 estimou quatro especificações por ciclo; a linha VD-1 é a razão de chances por +R$ 5 mil. *Resolução:* Só a especificação principal do E9 (logit condicional da 1ª opção, spline linear, bolsa linear), no ciclo 2 (VD-1) e nos ciclos empilhados (VD-2), como o script 42 fez no conjunto principal. O spline quadrático e os degraus por corte no conjunto de sensibilidade não são refeitos; os ciclos 1 e 3 não mudam por construção. Inferência como no doc 42 (cluster por conjunto de escolha). O score bootstrap e os placebos de corte do doc 42 foram usados só no conjunto principal (robustez pós-auditoria), nunca no de sensibilidade, e por isso não entram aqui.
3. **Alcance do VD-3** (26/10/2026). O §2 pede M2, M4, M6, M7, M8 e M9 "nos ciclos e no empilhado em que usam o tipo de vaga". *Resolução:* No P1 essas variantes só existem empilhadas, e todas usam o tipo de vaga do ciclo 2 (seção 3): M2, M4, M6 da nota, do município e do curso, M7, M8 e M9. O M3 não foi estimado no P1 e continua fora. O M1 e o M5 do ciclo 2 já foram corrigidos pelo adendo 52c; aqui são reestimados só como base da DAP, dos km, do M8 e do M9 e como membros das famílias BKY, e o script confere que saem iguais ao `VC_estimativas.csv` nas duas versões. O M5 dos ciclos 1 e 3 entra só no Wald e no BKY e tem de sair idêntico nas duas versões.
4. **Alcance do VD-4** (26/10/2026). O §2 diz "DAP e km equivalentes que dependem de VD-3", mas os km equivalentes (P1h-2) só existem no M1, e a DAP do M1 e a do M5 também usam o tipo de vaga e não foram refeitas pelo 52c (doc 57p, §7). *Resolução:* VD-4 = toda linha de DAP e de km que usa o tipo de vaga do ciclo 2 e ainda não tinha versão corrigida: DAP do M1 (delta e bootstrap de pares por conjunto, 999 réplicas, mesma semente do script 25), do M4, do M7 e do M5 do ciclo 2; K5 e K10 (M1); D_UF do P1h-3 no M2, no M4 e no M7. As DAP do M5 nos ciclos 1 e 3 não usam o ciclo 2 e não são refeitas. M8 e M9 não têm DAP nem D_UF nos originais e continuam sem.
5. **BKY nas secundárias** (26/10/2026). O §2 pede "BKY entre as secundárias" sem listar a família; o script 42 deixou pendentes as famílias BKY dos protocolos de origem, porque parte delas não estava no 52c. *Resolução:* Refazer as duas famílias exatamente como nos originais, com as linhas corrigidas no lugar das antigas: (a) família secundária do P1 (protocolo 52): β da bolsa no M5 por ciclo, Wald do P1d, interações e Wald do M6 da nota, interação do M6 do município, média da bolsa e desvios no M8; (b) família P1h-3 (protocolo 52b): D_UF, p unilateral, no M2, no M4, no M5 por ciclo e no M7. As linhas do E9 (VD-1, VD-2) ficam sem correção múltipla, como no protocolo 40 (§12) e no script 42. DAP e km continuam descritivos, sem teste, como nos originais. Não se cria família nova.
6. **Tolerância do portão** (26/10/2026). O §4 pede diferença ≤ 1e−8; os CSV de origem gravam 10 algarismos significativos, e para valores com módulo acima de 1 (DAP, km, Wald, log-verossimilhança) a diferença absoluta de 1e−8 fica abaixo da precisão gravada. *Resolução:* Diferença absoluta ≤ 1e−8 quando o valor gravado tem módulo ≤ 1, e relativa ≤ 1e−8 quando tem módulo maior; NaN só casa com NaN. Entram todas as linhas VD-5 (coeficientes, os três EP, IC, p, Wald, q BKY, DAP com IC delta e bootstrap, km com Fieller, D_UF). Qualquer falha para a execução antes da versão corrigida, e as saídas calculadas são apagadas.
7. **M8 e M9** (26/10/2026). O logit misto e o aninhado têm tetos de avaliações e polimento por Newton no script 25. *Resolução:* Mesmas funções (`estimar_misto`, `estimar_aninhado`), mesmos tetos, sementes e polimento, partindo do M1 da mesma versão. Se a versão corrigida não convergir, a linha fica NAO_CONVERGIU com o motivo; nada é forçado.
8. **Leitura do §3 por regra** (26/10/2026). O §3 fixa a leitura do VD-1 e do VD-3, mas não o critério de "sinal" e de "significância". *Resolução:* VD-1 'mantém' quando o IC 95% da razão de chances corrigida exclui 1 e o log da razão tem o mesmo sinal do antigo; 'dependia do quadro pós-resultado' quando o IC corrigido contém 1; IC que exclui 1 com sinal oposto não está no §3 e é relatado como 'sinal oposto', sem leitura. VD-3: uma variante muda de sinal quando a estimativa pontual de algum peso da bolsa dela muda de sinal (β da bolsa; média no M8; inclinações e interações no M6); a leitura da H2 lista as que não mudam. Mudança de significância compara, nas duas versões, o mesmo critério: q BKY < 0,05 nas linhas das famílias BKY; IC 95% com cluster por conjunto que exclui 0 (ou 1, na razão de chances) nas demais; p de máxima verossimilhança < 0,05 no M6 do curso (cluster degenerado, como no P1); IC delta (e, no M1, também o do bootstrap) na DAP e nos km.
9. **Razão de chances das variantes** (26/10/2026). O P1 não gravou razão de chances. *Resolução:* exp(5·β) com o IC transformado do IC do coeficiente, como no script 42; no M8, com a média da bolsa; no M9, com o β da utilidade do logit aninhado (descritiva).
10. **Números do doc 57v** (26/10/2026). O pedido do autor exige números só em blocos gerados. *Resolução:* Todo número de resultado do 57v vem de `VD_*` por `--atualizar-doc`, entre marcadores `<!-- VD:... -->`; o teste confere o doc contra o gerado e que não há número de resultado fora dos blocos.
<!-- VD:decisoes:fim -->

## 8. Limites

- **Pós-resultado.** As versões antigas e as principais corrigidas já eram conhecidas. O adendo foi congelado antes de rodar, mas as sensibilidades corrigidas não são teste confirmatório novo.
- **Só o tipo de vaga do ciclo 2 muda.** As linhas fora do §1 do adendo (seção 3) continuam com o quadro de 19/03; os placebos de corte, o score bootstrap e o spline cúbico do doc 42 não foram refeitos no conjunto só com vaga imediata.
- **O quadro de 13/02 também é anúncio.** Ele mede o que estava publicado na inscrição, não a vaga que de fato seria preenchida; o remanejamento posterior fica fora do atributo, como deve ficar num controle pré-tratamento.
- **O conjunto só com vaga imediata muda de tamanho.** Com o quadro de 13/02 ele perde as células de reserva que viraram imediatas depois do resultado e os candidatos que as escolheram; a comparação antiga × corrigida mistura a troca da covariável com a troca da amostra.
- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo; o conjunto de escolha supõe que o candidato viu todas as células do curso; IIA do logit condicional (relaxada em parte no M8 e no M9).
- **Pacote do corte.** O peso da bolsa é identificado pelos saltos nos cortes de IVS, com o IVS em spline contínua; nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no PMM-E nem do Agora Tem Especialistas.
- **Origem não é causal.** θ_UF é preferência revelada condicional ao modelo; a origem é o município do vínculo médico no CNES, não a residência.
- **DAP e km são razões.** Com o coeficiente da bolsa perto de zero, a razão fica instável e não é preço.
- **Poucos conjuntos.** O cluster é o conjunto de escolha (curso × ciclo), e são poucos; o número de cada linha está na coluna `g_conjuntos` de `VD_estimativas.csv`, e o p pela t com G − 1 gl está ao lado.
