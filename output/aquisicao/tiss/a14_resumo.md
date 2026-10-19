# A14 — resumo gerado do TISS/ANS

Gerado por `scripts/aquisicao/a14_adquirir_tiss_ans.py` em 2026-10-19. Não editar à mão. Natureza dos dados: EMPIRICO. Totais nacionais e cobertura por UF × mês; nada por faixa, corte ou tratamento.

## Cobertura (pacotes UF × mês)

| Base | Status | Pacotes |
|---|---|---:|
| AMB | aprovado | 1.296 |
| HOSP | aprovado | 1.296 |

### Meses com todas as 27 UFs aprovadas

| Base | Meses completos | Primeiro | Último |
|---|---:|---|---|
| AMB | 48 | 202201 | 202512 |
| HOSP | 48 | 202201 | 202512 |

## Validações

- Junção DET → CONS por pacote aprovado: mínima 1,0000, máxima 1,0000; pacotes com junção < 1: 0; linhas DET não juntadas: 0.
- Eventos CONS sem item DET: 0.
- Eventos de operadoras odontológicas excluídos: 76.454.398.
- Alertas de queda ou salto (base × UF × mês): 49.

### Eventos por status do município (pacotes aprovados, todas as operadoras)

| Status | Eventos |
|---|---:|
| municipio_invalido | 649 |
| municipio_omitido_pela_ans | 10.472 |
| ok | 2.968.012.743 |

### Quantidades informadas (linhas DET)

| Caso | Linhas |
|---|---:|
| det_mes_divergente | 0 |
| qt_nao_inteira | 3.713.345 |
| qt_nao_numerica | 0 |
| qt_negativa | 0 |
| qt_vazia_fora_de_pacote | 0 |
| qt_vazia_item_de_pacote | 445.976.575 |

### Linhas DET por tabela TUSS

| Tabela | Linhas |
|---|---:|
| 00 | 235.439.239 |
| 18 | 1.481 |
| 19 | 235.666 |
| 20 | 43.159.208 |
| 22 | 4.870.922.972 |
| 63 | 984.732.374 |
| 90 | 65.147.394 |
| 98 | 207.010.723 |

### Linhas DET da TUSS 22 por capítulo

| Capítulo | Linhas |
|---|---:|
| 1 | 1.031.610.238 |
| 2 | 200.025.682 |
| 3 | 105.050.964 |
| 4 | 2.751.665.373 |
| 5 | 215.580.654 |
| 8 | 566.990.061 |

## Participação de cada grupo de CBO nos eventos ambulatoriais atribuídos (todos os meses)

Fração de `n_eventos` do grupo sobre `todos_cbo`, por tipo; `mfc_225130` está contida em `especialistas_nao_alvo`.

| Tipo | alvo_pmme | especialistas_nao_alvo | mfc_225130 | generalistas | outros_medicos | nao_medicos | cbo_ausente |
|---|---:|---:|---:|---:|---:|---:|---:|
| consultas | 0,2366 | 0,4340 | 0,0085 | 0,2538 | 0,0006 | 0,0070 | 0,0681 |
| exames | 0,1495 | 0,1132 | 0,0006 | 0,1320 | 0,0001 | 0,0147 | 0,5904 |
| cirurgicos | 0,0692 | 0,2688 | 0,0006 | 0,0454 | 0,0001 | 0,0342 | 0,5823 |
| outros | 0,0842 | 0,1202 | 0,0020 | 0,1721 | 0,0001 | 0,0937 | 0,5296 |
| agrupados_tuss63 | 0,1016 | 0,1238 | 0,0009 | 0,1864 | 0,0001 | 0,0357 | 0,5524 |
| todos_nao_odonto | 0,1527 | 0,2244 | 0,0041 | 0,1764 | 0,0003 | 0,0521 | 0,3941 |

## Eventos por mês, Brasil, AMB (todos os CBO, inclusive não atribuídos; sem operadoras odontológicas)

Só meses com pacotes aprovados entram na soma; mês incompleto é marcado.

| Mês | Completo | evento_qualquer | todos_nao_odonto | consultas | exames | cirurgicos | outros |
|---|---|---:|---:|---:|---:|---:|---:|
| 202201 | sim | 51.587.057 | 50.808.040 | 19.480.177 | 13.863.384 | 1.033.338 | 25.163.719 |
| 202202 | sim | 49.486.019 | 48.598.707 | 17.313.134 | 13.266.571 | 1.125.848 | 24.793.312 |
| 202203 | sim | 57.152.869 | 56.162.741 | 20.501.618 | 14.832.197 | 1.350.607 | 28.694.029 |
| 202204 | sim | 51.799.032 | 50.892.605 | 18.601.149 | 13.372.345 | 1.213.399 | 26.367.582 |
| 202205 | sim | 59.225.135 | 58.218.615 | 21.577.073 | 15.019.131 | 1.361.596 | 29.913.807 |
| 202206 | sim | 56.018.925 | 55.261.152 | 20.630.260 | 14.393.086 | 1.271.457 | 28.175.857 |
| 202207 | sim | 55.538.594 | 54.532.061 | 19.740.018 | 14.516.896 | 1.280.385 | 28.134.404 |
| 202208 | sim | 60.223.079 | 59.092.744 | 21.417.328 | 15.041.037 | 1.475.153 | 30.564.455 |
| 202209 | sim | 55.397.706 | 54.349.627 | 19.587.408 | 13.701.388 | 1.378.164 | 28.529.311 |
| 202210 | sim | 56.096.960 | 55.096.999 | 19.857.009 | 14.331.589 | 1.415.451 | 28.752.771 |
| 202211 | sim | 56.701.803 | 55.728.179 | 20.006.721 | 14.958.782 | 1.404.749 | 28.721.853 |
| 202212 | sim | 48.194.650 | 47.351.907 | 17.712.045 | 12.921.684 | 1.206.124 | 23.597.770 |
| 202301 | sim | 55.819.469 | 54.870.781 | 20.027.196 | 15.840.259 | 1.377.693 | 27.256.902 |
| 202302 | sim | 51.890.523 | 50.951.207 | 18.728.107 | 14.386.042 | 1.296.284 | 25.496.375 |
| 202303 | sim | 66.755.694 | 65.661.334 | 24.833.826 | 18.262.725 | 1.669.684 | 32.205.598 |
| 202304 | sim | 55.440.237 | 54.434.568 | 20.028.034 | 15.293.738 | 1.365.291 | 27.495.355 |
| 202305 | sim | 63.742.095 | 62.606.614 | 23.489.474 | 17.212.618 | 1.602.666 | 31.022.754 |
| 202306 | sim | 58.709.633 | 57.626.179 | 21.493.702 | 15.845.978 | 1.483.831 | 28.545.828 |
| 202307 | sim | 59.366.736 | 58.232.734 | 20.913.869 | 16.250.954 | 1.486.559 | 29.436.482 |
| 202308 | sim | 64.653.620 | 63.379.459 | 23.029.723 | 17.394.872 | 1.680.829 | 31.545.230 |
| 202309 | sim | 56.877.813 | 55.764.993 | 20.031.995 | 15.634.461 | 1.473.251 | 28.113.301 |
| 202310 | sim | 58.958.821 | 57.805.569 | 21.025.145 | 16.136.421 | 1.564.804 | 28.863.690 |
| 202311 | sim | 56.772.216 | 55.722.590 | 20.366.386 | 15.554.526 | 1.494.727 | 27.888.390 |
| 202312 | sim | 48.124.423 | 47.219.379 | 17.342.219 | 12.992.870 | 1.238.993 | 23.851.441 |
| 202401 | sim | 57.897.100 | 56.885.800 | 20.738.935 | 16.536.332 | 1.356.785 | 28.299.732 |
| 202402 | sim | 56.752.821 | 55.748.520 | 20.286.024 | 16.211.583 | 1.359.239 | 27.918.758 |
| 202403 | sim | 62.384.824 | 61.341.477 | 22.368.047 | 18.085.976 | 1.482.046 | 30.863.829 |
| 202404 | sim | 66.997.518 | 65.887.453 | 24.472.020 | 18.851.481 | 1.596.786 | 32.938.249 |
| 202405 | sim | 62.729.692 | 61.640.648 | 22.394.063 | 17.578.540 | 1.490.861 | 31.307.893 |
| 202406 | sim | 60.626.251 | 59.577.486 | 21.702.198 | 16.869.228 | 1.477.688 | 30.147.805 |
| 202407 | sim | 64.548.173 | 63.391.774 | 22.596.558 | 18.100.917 | 1.598.324 | 32.011.349 |
| 202408 | sim | 65.622.010 | 64.428.115 | 23.134.493 | 18.233.263 | 1.633.655 | 32.608.501 |
| 202409 | sim | 63.897.684 | 62.784.725 | 22.676.966 | 17.607.155 | 1.567.595 | 31.884.694 |
| 202410 | sim | 67.212.858 | 66.016.856 | 23.713.910 | 18.423.866 | 1.722.691 | 33.480.629 |
| 202411 | sim | 59.725.954 | 58.637.749 | 20.800.088 | 16.679.083 | 1.525.929 | 29.845.971 |
| 202412 | sim | 51.120.691 | 50.247.779 | 18.296.332 | 13.912.983 | 1.243.059 | 25.352.531 |
| 202501 | sim | 61.750.057 | 60.702.902 | 21.701.047 | 18.030.194 | 1.394.813 | 30.104.984 |
| 202502 | sim | 62.829.295 | 61.676.925 | 21.390.173 | 18.096.547 | 1.483.471 | 31.083.489 |
| 202503 | sim | 62.639.105 | 61.614.914 | 21.532.676 | 18.076.774 | 1.457.437 | 31.423.623 |
| 202504 | sim | 65.103.968 | 64.048.312 | 22.524.295 | 18.313.219 | 1.540.286 | 32.652.779 |
| 202505 | sim | 68.361.689 | 67.255.623 | 24.194.329 | 19.360.779 | 1.583.201 | 33.871.765 |
| 202506 | sim | 62.069.125 | 61.020.952 | 21.713.774 | 17.292.831 | 1.460.149 | 30.831.585 |
| 202507 | sim | 67.489.376 | 66.276.186 | 22.887.325 | 19.138.075 | 1.591.483 | 33.750.391 |
| 202508 | sim | 67.102.142 | 65.685.042 | 22.932.459 | 18.571.652 | 1.597.782 | 33.704.054 |
| 202509 | sim | 69.953.972 | 68.743.665 | 24.053.637 | 19.215.398 | 1.679.678 | 35.230.731 |
| 202510 | sim | 70.297.083 | 69.259.327 | 24.232.754 | 19.501.451 | 1.696.372 | 35.371.526 |
| 202511 | sim | 59.090.664 | 57.861.886 | 20.100.028 | 16.409.351 | 1.408.406 | 29.930.566 |
| 202512 | sim | 49.477.612 | 48.562.411 | 17.577.263 | 12.970.043 | 1.187.672 | 24.962.057 |

## Eventos por mês, Brasil, HOSP (todos os CBO, inclusive não atribuídos; sem operadoras odontológicas)

Só meses com pacotes aprovados entram na soma; mês incompleto é marcado.

| Mês | Completo | evento_qualquer | todos_nao_odonto | consultas | exames | cirurgicos | outros |
|---|---|---:|---:|---:|---:|---:|---:|
| 202201 | sim | 531.933 | 531.931 | 186.601 | 162.469 | 225.843 | 486.523 |
| 202202 | sim | 509.359 | 509.357 | 166.716 | 150.166 | 228.362 | 467.261 |
| 202203 | sim | 606.540 | 606.540 | 204.714 | 175.351 | 278.898 | 559.225 |
| 202204 | sim | 575.384 | 575.383 | 201.328 | 174.120 | 253.004 | 532.422 |
| 202205 | sim | 635.668 | 635.668 | 215.636 | 189.774 | 274.626 | 582.963 |
| 202206 | sim | 639.502 | 639.502 | 205.049 | 180.971 | 261.490 | 588.054 |
| 202207 | sim | 650.927 | 650.925 | 199.462 | 178.107 | 277.483 | 597.986 |
| 202208 | sim | 672.397 | 672.397 | 200.949 | 179.564 | 293.081 | 620.169 |
| 202209 | sim | 643.515 | 643.515 | 199.154 | 171.434 | 281.754 | 592.654 |
| 202210 | sim | 657.312 | 657.312 | 208.475 | 175.445 | 285.881 | 605.858 |
| 202211 | sim | 646.868 | 646.868 | 205.908 | 176.969 | 290.579 | 594.466 |
| 202212 | sim | 594.672 | 594.672 | 201.950 | 170.473 | 252.783 | 543.083 |
| 202301 | sim | 661.038 | 661.037 | 208.129 | 178.133 | 301.455 | 604.623 |
| 202302 | sim | 584.382 | 584.381 | 193.962 | 163.826 | 253.294 | 535.459 |
| 202303 | sim | 715.905 | 715.904 | 232.311 | 198.380 | 308.339 | 658.350 |
| 202304 | sim | 638.963 | 638.962 | 218.641 | 184.150 | 265.879 | 586.793 |
| 202305 | sim | 687.739 | 687.739 | 230.360 | 194.541 | 297.894 | 633.512 |
| 202306 | sim | 659.170 | 659.170 | 218.276 | 184.021 | 293.842 | 608.483 |
| 202307 | sim | 674.385 | 674.385 | 215.856 | 183.123 | 307.944 | 623.263 |
| 202308 | sim | 714.972 | 714.972 | 219.204 | 189.020 | 326.976 | 658.681 |
| 202309 | sim | 649.716 | 649.715 | 203.653 | 175.806 | 293.807 | 595.683 |
| 202310 | sim | 671.026 | 671.023 | 212.061 | 179.132 | 306.422 | 617.712 |
| 202311 | sim | 656.509 | 656.507 | 209.119 | 174.995 | 303.297 | 606.309 |
| 202312 | sim | 596.947 | 596.947 | 199.209 | 165.920 | 261.038 | 548.933 |
| 202401 | sim | 667.751 | 667.751 | 213.627 | 182.511 | 306.239 | 614.121 |
| 202402 | sim | 636.878 | 636.877 | 216.036 | 180.928 | 283.130 | 586.092 |
| 202403 | sim | 701.433 | 701.431 | 246.581 | 206.798 | 298.651 | 647.989 |
| 202404 | sim | 731.374 | 731.373 | 254.508 | 213.523 | 309.622 | 675.099 |
| 202405 | sim | 713.260 | 713.259 | 248.293 | 209.233 | 299.372 | 654.490 |
| 202406 | sim | 661.091 | 661.090 | 221.602 | 191.079 | 287.849 | 606.726 |
| 202407 | sim | 720.286 | 720.286 | 224.464 | 197.744 | 324.937 | 658.368 |
| 202408 | sim | 724.464 | 724.464 | 228.647 | 203.067 | 323.331 | 660.997 |
| 202409 | sim | 699.786 | 699.785 | 227.592 | 199.225 | 307.655 | 640.255 |
| 202410 | sim | 719.546 | 719.544 | 231.083 | 203.407 | 330.379 | 663.628 |
| 202411 | sim | 679.821 | 679.820 | 220.782 | 196.006 | 303.105 | 629.100 |
| 202412 | sim | 616.075 | 616.075 | 218.596 | 189.831 | 258.790 | 573.465 |
| 202501 | sim | 665.613 | 665.613 | 226.258 | 197.642 | 308.221 | 622.932 |
| 202502 | sim | 625.612 | 625.610 | 213.969 | 185.046 | 295.350 | 587.508 |
| 202503 | sim | 626.404 | 626.403 | 231.863 | 192.498 | 295.118 | 591.517 |
| 202504 | sim | 648.520 | 648.518 | 240.900 | 200.368 | 304.877 | 608.509 |
| 202505 | sim | 701.914 | 701.913 | 253.524 | 215.655 | 326.421 | 648.430 |
| 202506 | sim | 671.460 | 671.459 | 237.709 | 210.383 | 312.240 | 614.895 |
| 202507 | sim | 720.160 | 720.159 | 240.920 | 218.060 | 354.866 | 662.547 |
| 202508 | sim | 707.527 | 707.527 | 239.457 | 214.188 | 343.813 | 654.285 |
| 202509 | sim | 682.734 | 682.731 | 232.338 | 207.271 | 334.984 | 634.395 |
| 202510 | sim | 679.508 | 679.507 | 229.836 | 207.338 | 336.591 | 629.196 |
| 202511 | sim | 581.355 | 581.349 | 200.445 | 175.055 | 292.477 | 537.082 |
| 202512 | sim | 499.292 | 499.291 | 175.675 | 160.384 | 243.945 | 458.312 |

## Comparação com o SIP (descritiva, não é portão)

| Trimestre | Item SIP | TISS | Medida | Completo | TISS | SIP | Razão | Alerta |
|---|---|---|---|---|---:|---:|---:|---|
| 202201 | A consultas médicas | AMB consultas | qt_itens | sim | 54.793.515,5701 | 62.681.521,0000 | 0,8742 | False |
| 202201 | A consultas médicas | AMB consultas | n_eventos | sim | 57.294.929,0000 | 62.681.521,0000 | 0,9141 | False |
| 202201 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.647.832,0000 | 1.943.104,0000 | 0,8480 | False |
| 202201 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 733.103,0000 | 828.237,0000 | 0,8851 | False |
| 202204 | A consultas médicas | AMB consultas | qt_itens | sim | 58.016.621,4333 | 67.841.107,0000 | 0,8552 | False |
| 202204 | A consultas médicas | AMB consultas | n_eventos | sim | 60.808.482,0000 | 67.841.107,0000 | 0,8963 | False |
| 202204 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.850.554,0000 | 2.240.212,0000 | 0,8261 | False |
| 202204 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 789.120,0000 | 982.170,0000 | 0,8034 | False |
| 202207 | A consultas médicas | AMB consultas | qt_itens | sim | 58.077.082,7100 | 69.358.550,0000 | 0,8373 | False |
| 202207 | A consultas médicas | AMB consultas | n_eventos | sim | 60.744.754,0000 | 69.358.550,0000 | 0,8758 | False |
| 202207 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.966.839,0000 | 2.278.318,0000 | 0,8633 | False |
| 202207 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 852.318,0000 | 1.028.177,0000 | 0,8290 | False |
| 202210 | A consultas médicas | AMB consultas | qt_itens | sim | 56.638.670,5500 | 64.798.897,0000 | 0,8741 | False |
| 202210 | A consultas médicas | AMB consultas | n_eventos | sim | 57.575.775,0000 | 64.798.897,0000 | 0,8885 | False |
| 202210 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.898.852,0000 | 2.305.899,0000 | 0,8235 | False |
| 202210 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 829.243,0000 | 1.053.469,0000 | 0,7872 | False |
| 202301 | A consultas médicas | AMB consultas | qt_itens | sim | 63.236.979,4266 | 65.044.743,0000 | 0,9722 | False |
| 202301 | A consultas médicas | AMB consultas | n_eventos | sim | 63.589.129,0000 | 65.044.743,0000 | 0,9776 | False |
| 202301 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.961.325,0000 | 2.170.238,0000 | 0,9037 | False |
| 202301 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 863.088,0000 | 998.371,0000 | 0,8645 | False |
| 202304 | A consultas médicas | AMB consultas | qt_itens | sim | 62.554.155,9376 | 72.767.031,0000 | 0,8596 | False |
| 202304 | A consultas médicas | AMB consultas | n_eventos | sim | 65.011.210,0000 | 72.767.031,0000 | 0,8934 | False |
| 202304 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.985.872,0000 | 2.301.392,0000 | 0,8629 | False |
| 202304 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 857.615,0000 | 1.053.670,0000 | 0,8139 | False |
| 202307 | A consultas médicas | AMB consultas | qt_itens | sim | 61.216.416,2976 | 70.494.926,0000 | 0,8684 | False |
| 202307 | A consultas médicas | AMB consultas | n_eventos | sim | 63.975.587,0000 | 70.494.926,0000 | 0,9075 | False |
| 202307 | E internações | HOSP evento_qualquer | n_eventos | sim | 2.039.073,0000 | 2.410.011,0000 | 0,8461 | False |
| 202307 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 928.727,0000 | 1.131.516,0000 | 0,8208 | False |
| 202310 | A consultas médicas | AMB consultas | qt_itens | sim | 55.785.117,7195 | 67.013.116,0000 | 0,8325 | False |
| 202310 | A consultas médicas | AMB consultas | n_eventos | sim | 58.733.750,0000 | 67.013.116,0000 | 0,8765 | False |
| 202310 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.924.482,0000 | 2.306.450,0000 | 0,8344 | False |
| 202310 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 870.757,0000 | 1.078.433,0000 | 0,8074 | False |
| 202401 | A consultas médicas | AMB consultas | qt_itens | sim | 60.002.612,0000 | 66.308.328,0000 | 0,9049 | False |
| 202401 | A consultas médicas | AMB consultas | n_eventos | sim | 63.393.006,0000 | 66.308.328,0000 | 0,9560 | False |
| 202401 | E internações | HOSP evento_qualquer | n_eventos | sim | 2.006.062,0000 | 2.171.829,0000 | 0,9237 | False |
| 202401 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 888.020,0000 | 1.013.990,0000 | 0,8758 | False |
| 202404 | A consultas médicas | AMB consultas | qt_itens | sim | 64.742.667,3979 | 74.931.894,0000 | 0,8640 | False |
| 202404 | A consultas médicas | AMB consultas | n_eventos | sim | 68.568.281,0000 | 74.931.894,0000 | 0,9151 | False |
| 202404 | E internações | HOSP evento_qualquer | n_eventos | sim | 2.105.725,0000 | 2.295.135,0000 | 0,9175 | False |
| 202404 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 896.843,0000 | 1.046.814,0000 | 0,8567 | False |
| 202407 | A consultas médicas | AMB consultas | qt_itens | sim | 64.705.774,0238 | 72.631.769,0000 | 0,8909 | False |
| 202407 | A consultas médicas | AMB consultas | n_eventos | sim | 68.408.017,0000 | 72.631.769,0000 | 0,9418 | False |
| 202407 | E internações | HOSP evento_qualquer | n_eventos | sim | 2.144.536,0000 | 2.278.832,0000 | 0,9411 | False |
| 202407 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 955.923,0000 | 1.076.559,0000 | 0,8879 | False |
| 202410 | A consultas médicas | AMB consultas | qt_itens | sim | 59.428.361,1050 | 70.665.391,0000 | 0,8410 | False |
| 202410 | A consultas médicas | AMB consultas | n_eventos | sim | 62.810.330,0000 | 70.665.391,0000 | 0,8888 | False |
| 202410 | E internações | HOSP evento_qualquer | n_eventos | sim | 2.015.442,0000 | 2.352.286,0000 | 0,8568 | False |
| 202410 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 892.274,0000 | 1.103.373,0000 | 0,8087 | False |
| 202501 | A consultas médicas | AMB consultas | qt_itens | sim | 61.196.468,1633 | 67.533.809,0000 | 0,9062 | False |
| 202501 | A consultas médicas | AMB consultas | n_eventos | sim | 64.623.896,0000 | 67.533.809,0000 | 0,9569 | False |
| 202501 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.917.629,0000 | 2.315.999,0000 | 0,8280 | False |
| 202501 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 898.689,0000 | 1.115.543,0000 | 0,8056 | False |
| 202504 | A consultas médicas | AMB consultas | qt_itens | sim | 64.371.204,4553 | 72.324.448,0000 | 0,8900 | False |
| 202504 | A consultas médicas | AMB consultas | n_eventos | sim | 68.432.398,0000 | 72.324.448,0000 | 0,9462 | False |
| 202504 | E internações | HOSP evento_qualquer | n_eventos | sim | 2.021.894,0000 | 2.395.692,0000 | 0,8440 | False |
| 202504 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 943.538,0000 | 1.140.524,0000 | 0,8273 | False |
| 202507 | A consultas médicas | AMB consultas | qt_itens | sim | 65.875.646,4300 | 76.372.687,0000 | 0,8626 | False |
| 202507 | A consultas médicas | AMB consultas | n_eventos | sim | 69.873.421,0000 | 76.372.687,0000 | 0,9149 | False |
| 202507 | E internações | HOSP evento_qualquer | n_eventos | sim | 2.110.421,0000 | 2.607.134,0000 | 0,8095 | False |
| 202507 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 1.033.663,0000 | 1.261.608,0000 | 0,8193 | False |
| 202510 | A consultas médicas | AMB consultas | qt_itens | sim | 58.049.809,6746 | 72.492.774,0000 | 0,8008 | False |
| 202510 | A consultas médicas | AMB consultas | n_eventos | sim | 61.910.045,0000 | 72.492.774,0000 | 0,8540 | False |
| 202510 | E internações | HOSP evento_qualquer | n_eventos | sim | 1.760.155,0000 | 2.592.035,0000 | 0,6791 | False |
| 202510 | E1.02 internações cirúrgicas | HOSP cirurgicos | n_eventos | sim | 873.013,0000 | 1.279.410,0000 | 0,6824 | False |

## Alertas de queda ou salto (sinalizados, não corrigidos)

| Base | UF | Mês | Eventos | Mediana da UF | Motivos |
|---|---|---|---:|---:|---|
| AMB | AC | 202509 | 28.298 | 44.334,5000 | queda_de_mais_de_40pct_contra_202508 |
| AMB | AC | 202510 | 13.079 | 44.334,5000 | abaixo_de_metade_da_mediana_da_uf, queda_de_mais_de_40pct_contra_202509 |
| AMB | AC | 202511 | 11.062 | 44.334,5000 | abaixo_de_metade_da_mediana_da_uf |
| AMB | AC | 202512 | 10.056 | 44.334,5000 | abaixo_de_metade_da_mediana_da_uf |
| AMB | PI | 202211 | 1.865.090 | 466.700,0000 | acima_do_dobro_da_mediana_da_uf |
| AMB | PI | 202212 | 523.611 | 466.700,0000 | queda_de_mais_de_40pct_contra_202211 |
| AMB | PI | 202307 | 1.011.296 | 466.700,0000 | acima_do_dobro_da_mediana_da_uf |
| AMB | PI | 202308 | 447.532 | 466.700,0000 | queda_de_mais_de_40pct_contra_202307 |
| AMB | PI | 202402 | 439.292 | 466.700,0000 | queda_de_mais_de_40pct_contra_202401 |
| AMB | RR | 202511 | 18.016 | 31.339,0000 | queda_de_mais_de_40pct_contra_202510 |
| AMB | RR | 202512 | 13.500 | 31.339,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | AC | 202509 | 140 | 372,5000 | abaixo_de_metade_da_mediana_da_uf, queda_de_mais_de_40pct_contra_202508 |
| HOSP | AC | 202510 | 124 | 372,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | AC | 202511 | 102 | 372,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | AC | 202512 | 64 | 372,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | AL | 202206 | 17.130 | 7.217,0000 | acima_do_dobro_da_mediana_da_uf |
| HOSP | AL | 202502 | 3.606 | 7.217,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | AM | 202410 | 5.147 | 5.333,5000 | queda_de_mais_de_40pct_contra_202409 |
| HOSP | AP | 202206 | 735 | 885,5000 | queda_de_mais_de_40pct_contra_202205 |
| HOSP | AP | 202210 | 678 | 885,5000 | queda_de_mais_de_40pct_contra_202209 |
| HOSP | AP | 202302 | 944 | 885,5000 | queda_de_mais_de_40pct_contra_202301 |
| HOSP | AP | 202409 | 736 | 885,5000 | queda_de_mais_de_40pct_contra_202408 |
| HOSP | AP | 202511 | 371 | 885,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | AP | 202512 | 314 | 885,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | CE | 202501 | 12.169 | 25.983,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | CE | 202502 | 10.611 | 25.983,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | CE | 202503 | 11.177 | 25.983,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | MA | 202512 | 4.104 | 9.763,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | PI | 202512 | 2.076 | 4.687,5000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202202 | 123 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202203 | 75 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202204 | 72 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202205 | 96 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202206 | 107 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202207 | 89 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202208 | 85 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202209 | 92 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202210 | 85 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202211 | 111 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202212 | 122 | 256,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | RR | 202511 | 210 | 256,0000 | queda_de_mais_de_40pct_contra_202510 |
| HOSP | RR | 202512 | 47 | 256,0000 | abaixo_de_metade_da_mediana_da_uf, queda_de_mais_de_40pct_contra_202511 |
| HOSP | SE | 202204 | 3.490 | 7.094,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | SE | 202212 | 15.440 | 7.094,0000 | acima_do_dobro_da_mediana_da_uf |
| HOSP | SE | 202503 | 3.479 | 7.094,0000 | abaixo_de_metade_da_mediana_da_uf, queda_de_mais_de_40pct_contra_202502 |
| HOSP | SE | 202512 | 2.875 | 7.094,0000 | abaixo_de_metade_da_mediana_da_uf |
| HOSP | TO | 202303 | 3.413 | 1.471,5000 | acima_do_dobro_da_mediana_da_uf |
| HOSP | TO | 202309 | 1.097 | 1.471,5000 | queda_de_mais_de_40pct_contra_202308 |
| HOSP | TO | 202402 | 988 | 1.471,5000 | queda_de_mais_de_40pct_contra_202401 |
