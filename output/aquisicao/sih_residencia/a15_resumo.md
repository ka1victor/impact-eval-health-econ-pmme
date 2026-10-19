# A15 — resumo gerado do SIH/SUS por local de residência (TabNet)

Gerado por `scripts/aquisicao/a15_adquirir_sih_residencia.py` em 2026-10-19. Não editar à mão. Natureza dos dados: EMPIRICO. Totais nacionais e por UF apenas; nada por IVS, faixa ou lado de corte.

Status das validações: **APROVADO**. Universo: 5571 municípios (lista do formulário do TabNet).

## UF-mês sem arquivo de internação (NaN no painel, nunca zero nem parcial)

total de AIH aprovadas da UF no mês igual a zero na consulta contemporânea por local de internação (int_uf_grupo_aih, formulário qibr.def).

Nenhum.

## UF-mês de residência com total zero (NaN no painel)

Nenhum.

## UF-mês atípico (alerta; valor mantido): total da UF de internação no mês > 0 e < 0.5 × mediana mensal da UF em 202201–202607 (consulta contemporânea por local de internação); alerta (coluna uf_mes_atipico), o valor não é alterado

| Competência | UF | AIH da UF (internação) | AIH da UF (residência) | Mediana mensal (internação) | Fração |
|---|---|---:|---:|---:|---:|
| 202206 | RR | 668 | 770 | 3340 | 0.200 |
| 202309 | RR | 1535 | 1625 | 3340 | 0.460 |
| 202607 | RR | 515 | 650 | 3340 | 0.154 |

## Comparação com o a13 (total nacional de AIH aprovadas)

Validações do a13 lidas: SHA-256 `b2a42464b2dbcbe1…`. Meses iguais ao a13: 44. Meses revistos pela fonte depois da extração do a13: 202509, 202510, 202511, 202512, 202601, 202602, 202603, 202604, 202605, 202606, 202607.

| Competência | Total a13 (versionado) | Total por residência | Total por internação (mesma execução) | Diferença |
|---|---:|---:|---:|---:|
| 202509 | 1260380 | 1260437 | 1260437 | +57 |
| 202510 | 1273296 | 1273466 | 1273466 | +170 |
| 202511 | 1205099 | 1205485 | 1205485 | +386 |
| 202512 | 1174423 | 1174813 | 1174813 | +390 |
| 202601 | 1190325 | 1190819 | 1190819 | +494 |
| 202602 | 1155840 | 1156375 | 1156375 | +535 |
| 202603 | 1270554 | 1272425 | 1272425 | +1871 |
| 202604 | 1232976 | 1238763 | 1238763 | +5787 |
| 202605 | 1267230 | 1274466 | 1274466 | +7236 |
| 202606 | 1232141 | 1251609 | 1251609 | +19468 |
| 202607 | 1211160 | 1271615 | 1271615 | +60455 |

## Totais nacionais de AIH aprovadas por mês de processamento e grupo

Total do próprio TabNet (inclui município ignorado e exterior). Validações v1–v9 em `a15_validacoes.json`.

| Competência | Grupo 02 | Grupo 03 | Grupo 04 | Grupo 05 | Total | Municípios com AIH | Municípios com AIH do grupo 04 | v1 | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|---|---|
| 202201 | 1912 | 607498 | 373321 | 5576 | 988307 | 5570 | 5550 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202202 | 1789 | 575149 | 374383 | 5250 | 956571 | 5569 | 5556 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202203 | 2068 | 613028 | 417911 | 5869 | 1038876 | 5570 | 5560 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202204 | 2118 | 602374 | 413195 | 5664 | 1023351 | 5569 | 5562 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202205 | 2198 | 620838 | 426102 | 6181 | 1055319 | 5569 | 5559 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202206 | 2134 | 603894 | 421928 | 6057 | 1034013 | 5568 | 5559 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202207 | 2437 | 619981 | 448875 | 6026 | 1077319 | 5570 | 5564 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202208 | 2671 | 619823 | 471090 | 6628 | 1100212 | 5570 | 5563 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202209 | 2531 | 599283 | 463566 | 6383 | 1071763 | 5570 | 5565 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202210 | 2342 | 597287 | 468102 | 6160 | 1073891 | 5569 | 5565 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202211 | 2126 | 585624 | 450351 | 6231 | 1044332 | 5569 | 5561 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202212 | 2376 | 598938 | 449403 | 6243 | 1056960 | 5569 | 5563 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202301 | 2268 | 605526 | 438376 | 6279 | 1052449 | 5570 | 5561 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202302 | 2202 | 579689 | 424749 | 5836 | 1012476 | 5569 | 5560 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202303 | 2473 | 643648 | 479611 | 6459 | 1132191 | 5570 | 5564 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202304 | 2354 | 624534 | 452452 | 6601 | 1085941 | 5569 | 5562 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202305 | 2343 | 654929 | 487266 | 6787 | 1151325 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202306 | 2576 | 640630 | 483042 | 7040 | 1133288 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202307 | 2503 | 644100 | 497339 | 6792 | 1150734 | 5570 | 5559 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202308 | 2741 | 647573 | 518916 | 7023 | 1176253 | 5570 | 5564 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202309 | 2552 | 618322 | 500423 | 6660 | 1127957 | 5570 | 5567 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202310 | 2325 | 619274 | 503902 | 6877 | 1132378 | 5570 | 5570 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202311 | 2508 | 610035 | 494148 | 6720 | 1113411 | 5569 | 5567 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202312 | 2494 | 601881 | 476026 | 7010 | 1087411 | 5569 | 5564 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202401 | 2537 | 620097 | 480005 | 6455 | 1109094 | 5570 | 5569 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202402 | 2373 | 609133 | 476063 | 6565 | 1094134 | 5569 | 5564 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202403 | 2578 | 662485 | 513604 | 7292 | 1185959 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202404 | 2586 | 690948 | 524097 | 7231 | 1224862 | 5570 | 5567 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202405 | 2628 | 689257 | 520861 | 6943 | 1219689 | 5570 | 5565 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202406 | 2552 | 663327 | 515819 | 7192 | 1188890 | 5570 | 5562 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202407 | 2832 | 668540 | 541408 | 7300 | 1220080 | 5570 | 5566 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202408 | 2857 | 661069 | 557833 | 7459 | 1229218 | 5570 | 5564 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202409 | 2851 | 648668 | 547847 | 7202 | 1206568 | 5570 | 5569 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202410 | 2923 | 653857 | 560494 | 7345 | 1224619 | 5570 | 5569 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202411 | 2728 | 620019 | 527020 | 7047 | 1156814 | 5570 | 5563 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202412 | 2449 | 610432 | 491479 | 7077 | 1111437 | 5570 | 5565 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202501 | 2404 | 653067 | 501893 | 7290 | 1164654 | 5570 | 5566 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202502 | 2605 | 619419 | 501940 | 7010 | 1130974 | 5569 | 5566 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202503 | 2566 | 665829 | 519866 | 6762 | 1195023 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202504 | 2692 | 666091 | 524954 | 7513 | 1201250 | 5570 | 5566 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202505 | 2926 | 704306 | 557303 | 7441 | 1271976 | 5570 | 5567 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202506 | 2873 | 687864 | 533750 | 7526 | 1232013 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202507 | 2797 | 694922 | 568937 | 8040 | 1274696 | 5569 | 5567 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202508 | 3065 | 681592 | 570751 | 8313 | 1263721 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | igual |
| 202509 | 2980 | 672118 | 576912 | 8427 | 1260437 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202510 | 3025 | 677291 | 585311 | 7839 | 1273466 | 5570 | 5569 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202511 | 2948 | 642063 | 552471 | 8003 | 1205485 | 5570 | 5569 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202512 | 2693 | 641244 | 523399 | 7477 | 1174813 | 5570 | 5569 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202601 | 2493 | 652921 | 527721 | 7684 | 1190819 | 5570 | 5566 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202602 | 2501 | 626609 | 519907 | 7358 | 1156375 | 5570 | 5565 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202603 | 2908 | 683534 | 578197 | 7786 | 1272425 | 5568 | 5563 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202604 | 2511 | 672663 | 556297 | 7292 | 1238763 | 5569 | 5558 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202605 | 2813 | 682998 | 580467 | 8188 | 1274466 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202606 | 2945 | 674515 | 566469 | 7680 | 1251609 | 5570 | 5568 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |
| 202607 | 3196 | 672690 | 587675 | 8054 | 1271615 | 5569 | 5566 | ok | ok | ok | ok | ok | ok | ok | ok | revisado |

## Status no painel principal

| Status | Linhas |
|---|---:|
| observado | 746577 |
| zero_tabnet | 479043 |

## Caráter do atendimento (grupo 04)

| Código | Rótulo do TabNet |
|---|---|
| acid_local_trab | Acid local trab |
| acid_trajeto | Acid trajeto |
| eletivo | Eletivo |
| outras_caus_ext | Outras caus ext |
| outros_ac_trab | Outros ac trab |
| urgencia | Urgência |
