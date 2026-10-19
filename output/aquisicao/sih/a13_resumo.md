# A13 — resumo gerado do SIH/SUS (TabNet)

Gerado por `scripts/aquisicao/a13_adquirir_sih_tabnet.py` em 2026-10-19. Não editar à mão. Natureza dos dados: EMPIRICO. Totais nacionais e por UF apenas; nada por IVS, faixa ou lado de corte.

Status das validações: **APROVADO**. Universo: 5571 municípios (lista do formulário do TabNet).

## UF-mês sem dado na fonte (NaN no painel, nunca zero)

| Competência | UF |
|---|---|
| 202607 | AC (12) |
| 202607 | RR (14) |

## UF-mês atípico (alerta; valor mantido): total da UF no mês > 0 e < 0.5 × mediana mensal da UF em 202201–202607; alerta (coluna uf_mes_atipico), o valor não é alterado

| Competência | UF | AIH da UF | Mediana mensal da UF | Fração |
|---|---|---:|---:|---:|
| 202206 | RR | 668 | 3280 | 0.204 |
| 202309 | RR | 1535 | 3280 | 0.468 |
| 202606 | RR | 694 | 3280 | 0.212 |

## Totais nacionais de AIH aprovadas por mês de processamento e grupo

Total do próprio TabNet (inclui município ignorado e exterior). Validações v1–v7 em `a13_validacoes.json`.

| Competência | Grupo 02 | Grupo 03 | Grupo 04 | Grupo 05 | Total | Municípios com AIH | Municípios com AIH do grupo 04 | v1 | v2 | v3 | v4 | v5 | v6 | v7 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|
| 202201 | 1912 | 607498 | 373321 | 5576 | 988307 | 3024 | 1828 | ok | ok | ok | ok | ok | ok | ok |
| 202202 | 1789 | 575149 | 374383 | 5250 | 956571 | 3030 | 1874 | ok | ok | ok | ok | ok | ok | ok |
| 202203 | 2068 | 613028 | 417911 | 5869 | 1038876 | 3028 | 1890 | ok | ok | ok | ok | ok | ok | ok |
| 202204 | 2118 | 602374 | 413195 | 5664 | 1023351 | 3024 | 1891 | ok | ok | ok | ok | ok | ok | ok |
| 202205 | 2198 | 620838 | 426102 | 6181 | 1055319 | 3039 | 1873 | ok | ok | ok | ok | ok | ok | ok |
| 202206 | 2134 | 603894 | 421928 | 6057 | 1034013 | 3020 | 1886 | ok | ok | ok | ok | ok | ok | ok |
| 202207 | 2437 | 619981 | 448875 | 6026 | 1077319 | 3034 | 1893 | ok | ok | ok | ok | ok | ok | ok |
| 202208 | 2671 | 619823 | 471090 | 6628 | 1100212 | 3034 | 1907 | ok | ok | ok | ok | ok | ok | ok |
| 202209 | 2531 | 599283 | 463566 | 6383 | 1071763 | 3031 | 1922 | ok | ok | ok | ok | ok | ok | ok |
| 202210 | 2342 | 597287 | 468102 | 6160 | 1073891 | 3039 | 1924 | ok | ok | ok | ok | ok | ok | ok |
| 202211 | 2126 | 585624 | 450351 | 6231 | 1044332 | 3029 | 1896 | ok | ok | ok | ok | ok | ok | ok |
| 202212 | 2376 | 598938 | 449403 | 6243 | 1056960 | 3014 | 1906 | ok | ok | ok | ok | ok | ok | ok |
| 202301 | 2268 | 605526 | 438376 | 6279 | 1052449 | 3030 | 1891 | ok | ok | ok | ok | ok | ok | ok |
| 202302 | 2202 | 579689 | 424749 | 5836 | 1012476 | 3044 | 1907 | ok | ok | ok | ok | ok | ok | ok |
| 202303 | 2473 | 643648 | 479611 | 6459 | 1132191 | 3048 | 1916 | ok | ok | ok | ok | ok | ok | ok |
| 202304 | 2354 | 624534 | 452452 | 6601 | 1085941 | 3051 | 1919 | ok | ok | ok | ok | ok | ok | ok |
| 202305 | 2343 | 654929 | 487266 | 6787 | 1151325 | 3056 | 1917 | ok | ok | ok | ok | ok | ok | ok |
| 202306 | 2576 | 640630 | 483042 | 7040 | 1133288 | 3054 | 1924 | ok | ok | ok | ok | ok | ok | ok |
| 202307 | 2503 | 644100 | 497339 | 6792 | 1150734 | 3047 | 1931 | ok | ok | ok | ok | ok | ok | ok |
| 202308 | 2741 | 647573 | 518916 | 7023 | 1176253 | 3051 | 1937 | ok | ok | ok | ok | ok | ok | ok |
| 202309 | 2552 | 618322 | 500423 | 6660 | 1127957 | 3033 | 1933 | ok | ok | ok | ok | ok | ok | ok |
| 202310 | 2325 | 619274 | 503902 | 6877 | 1132378 | 3040 | 1940 | ok | ok | ok | ok | ok | ok | ok |
| 202311 | 2508 | 610035 | 494148 | 6720 | 1113411 | 3032 | 1934 | ok | ok | ok | ok | ok | ok | ok |
| 202312 | 2494 | 601881 | 476026 | 7010 | 1087411 | 3023 | 1927 | ok | ok | ok | ok | ok | ok | ok |
| 202401 | 2537 | 620097 | 480005 | 6455 | 1109094 | 3039 | 1944 | ok | ok | ok | ok | ok | ok | ok |
| 202402 | 2373 | 609133 | 476063 | 6565 | 1094134 | 3041 | 1927 | ok | ok | ok | ok | ok | ok | ok |
| 202403 | 2578 | 662485 | 513604 | 7292 | 1185959 | 3046 | 1943 | ok | ok | ok | ok | ok | ok | ok |
| 202404 | 2586 | 690948 | 524097 | 7231 | 1224862 | 3056 | 1958 | ok | ok | ok | ok | ok | ok | ok |
| 202405 | 2628 | 689257 | 520861 | 6943 | 1219689 | 3051 | 1969 | ok | ok | ok | ok | ok | ok | ok |
| 202406 | 2552 | 663327 | 515819 | 7192 | 1188890 | 3062 | 1955 | ok | ok | ok | ok | ok | ok | ok |
| 202407 | 2832 | 668540 | 541408 | 7300 | 1220080 | 3063 | 1973 | ok | ok | ok | ok | ok | ok | ok |
| 202408 | 2857 | 661069 | 557833 | 7459 | 1229218 | 3054 | 1973 | ok | ok | ok | ok | ok | ok | ok |
| 202409 | 2851 | 648668 | 547847 | 7202 | 1206568 | 3067 | 1961 | ok | ok | ok | ok | ok | ok | ok |
| 202410 | 2923 | 653857 | 560494 | 7345 | 1224619 | 3068 | 1967 | ok | ok | ok | ok | ok | ok | ok |
| 202411 | 2728 | 620019 | 527020 | 7047 | 1156814 | 3057 | 1948 | ok | ok | ok | ok | ok | ok | ok |
| 202412 | 2449 | 610432 | 491479 | 7077 | 1111437 | 3015 | 1891 | ok | ok | ok | ok | ok | ok | ok |
| 202501 | 2404 | 653067 | 501893 | 7290 | 1164654 | 3053 | 1852 | ok | ok | ok | ok | ok | ok | ok |
| 202502 | 2605 | 619419 | 501940 | 7010 | 1130974 | 3054 | 1892 | ok | ok | ok | ok | ok | ok | ok |
| 202503 | 2566 | 665829 | 519866 | 6762 | 1195023 | 3067 | 1913 | ok | ok | ok | ok | ok | ok | ok |
| 202504 | 2692 | 666091 | 524954 | 7513 | 1201250 | 3083 | 1930 | ok | ok | ok | ok | ok | ok | ok |
| 202505 | 2926 | 704306 | 557303 | 7441 | 1271976 | 3079 | 1930 | ok | ok | ok | ok | ok | ok | ok |
| 202506 | 2873 | 687864 | 533750 | 7526 | 1232013 | 3078 | 1948 | ok | ok | ok | ok | ok | ok | ok |
| 202507 | 2797 | 694922 | 568937 | 8040 | 1274696 | 3077 | 1966 | ok | ok | ok | ok | ok | ok | ok |
| 202508 | 3065 | 681592 | 570751 | 8313 | 1263721 | 3091 | 1963 | ok | ok | ok | ok | ok | ok | ok |
| 202509 | 2980 | 672061 | 576912 | 8427 | 1260380 | 3080 | 1972 | ok | ok | ok | ok | ok | ok | ok |
| 202510 | 3025 | 677182 | 585250 | 7839 | 1273296 | 3072 | 1954 | ok | ok | ok | ok | ok | ok | ok |
| 202511 | 2948 | 641890 | 552258 | 8003 | 1205099 | 3053 | 1954 | ok | ok | ok | ok | ok | ok | ok |
| 202512 | 2693 | 640900 | 523353 | 7477 | 1174423 | 3036 | 1926 | ok | ok | ok | ok | ok | ok | ok |
| 202601 | 2493 | 652595 | 527553 | 7684 | 1190325 | 3034 | 1887 | ok | ok | ok | ok | ok | ok | ok |
| 202602 | 2501 | 626335 | 519646 | 7358 | 1155840 | 3031 | 1908 | ok | ok | ok | ok | ok | ok | ok |
| 202603 | 2908 | 682186 | 577675 | 7785 | 1270554 | 3005 | 1937 | ok | ok | ok | ok | ok | ok | ok |
| 202604 | 2510 | 668828 | 554359 | 7279 | 1232976 | 2962 | 1905 | ok | ok | ok | ok | ok | ok | ok |
| 202605 | 2810 | 678568 | 577676 | 8176 | 1267230 | 2899 | 1870 | ok | ok | ok | ok | ok | ok | ok |
| 202606 | 2937 | 662112 | 559418 | 7674 | 1232141 | 2769 | 1805 | ok | ok | ok | ok | ok | ok | ok |
| 202607 | 3175 | 635288 | 564701 | 7996 | 1211160 | 2396 | 1613 | ok | ok | ok | ok | ok | ok | ok |

## Status no painel principal

| Status | Linhas |
|---|---:|
| ausente_uf_mes_sem_dado | 148 |
| observado | 290255 |
| zero_tabnet | 935217 |

## Caráter do atendimento (grupo 04)

| Código | Rótulo do TabNet |
|---|---|
| acid_local_trab | Acid local trab |
| acid_trajeto | Acid trajeto |
| eletivo | Eletivo |
| outras_caus_ext | Outras caus ext |
| outros_ac_trab | Outros ac trab |
| urgencia | Urgência |
