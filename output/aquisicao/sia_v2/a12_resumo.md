# A12 safra v2 — resumo gerado do SIA/SUS (TabNet)

Gerado por `scripts/aquisicao/a12b_safra_v2_sia.py` (lógica do a12) em 2026-10-19. Não editar à mão. Natureza dos dados: EMPIRICO. Só totais nacionais e contagens; nada por faixa, lado de corte ou IVS.

## Aquisição

- Meses de processamento: 11 (202509 a 202607).
- Consultas: 87, entre 2026-10-19T21:09:20+00:00 e 2026-10-19T21:15:49+00:00 (UTC); com mais de uma tentativa: 0.
- Municípios na lista do formulário: 5571.
- Linhas do painel: 14250618.

## Validações

| Validação | Status |
|---|---|
| V1_total_igual_soma_das_linhas | APROVADO |
| V2_conjuntos_le_todos | APROVADO |
| V3_todos_contra_consulta_uf | APROVADO |
| V4_conjunto_contra_soma_das_cbo | APROVADO |
| V5_conferencia_uf_celula_a_celula | APROVADO |
| V6_cobertura | RELATO |
| V7_eco_e_limites | APROVADO |

## Conjuntos de CBO

| Conjunto | CBO |
|---|---|
| alvo_pmme | 225120, 225121, 225148, 225151, 225165, 225220, 225225, 225250, 225255, 225275, 225280, 225290, 225305, 225310, 225320, 225325, 225330 |
| especialistas_nao_alvo | 225103, 225105, 225106, 225109, 225110, 225112, 225115, 225118, 225122, 225124, 225127, 225130, 225133, 225135, 225136, 225139, 225140, 225145, 225150, 225154, 225155, 225160, 225175, 225180, 225185, 225190, 225195, 225203, 225210, 225215, 225230, 225235, 225240, 225245, 225260, 225265, 225270, 225285, 225295, 225315, 225335, 225340, 225345, 225350, 225355 |
| generalistas | 225125, 225142, 225170 |
| mfc_225130 | 225130 |

## Cobertura por mês e conjunto

Municípios com produção = municípios com quantidade aprovada > 0 em algum subgrupo.

### alvo_pmme

| Mês | Municípios com produção | Qtd. municípios | Qtd. ignorados | Total TabNet | Subgrupos | Sinal |
|---|---:|---:|---:|---:|---:|---|
| 202509 | 3652 | 16424146 | 0 | 16424146 | 53 |  |
| 202510 | 3679 | 16373455 | 0 | 16373455 | 53 |  |
| 202511 | 3674 | 15165835 | 0 | 15165835 | 54 |  |
| 202512 | 3613 | 14388729 | 0 | 14388729 | 52 |  |
| 202601 | 3587 | 14209387 | 0 | 14209387 | 53 |  |
| 202602 | 3623 | 14064864 | 0 | 14064864 | 52 |  |
| 202603 | 3643 | 16485856 | 0 | 16485856 | 53 |  |
| 202604 | 3648 | 15822046 | 0 | 15822046 | 53 |  |
| 202605 | 3572 | 15747488 | 0 | 15747488 | 55 |  |
| 202606 | 3409 | 16010626 | 0 | 16010626 | 54 |  |
| 202607 | 2706 | 14174344 | 0 | 14174344 | 54 | municípios com produção < 90% da mediana do conjunto (3623) |

### especialistas_nao_alvo

| Mês | Municípios com produção | Qtd. municípios | Qtd. ignorados | Total TabNet | Subgrupos | Sinal |
|---|---:|---:|---:|---:|---:|---|
| 202509 | 3654 | 27825715 | 0 | 27825715 | 53 |  |
| 202510 | 3650 | 28668640 | 0 | 28668640 | 53 |  |
| 202511 | 3638 | 25483566 | 0 | 25483566 | 53 |  |
| 202512 | 3598 | 23102483 | 0 | 23102483 | 53 |  |
| 202601 | 3506 | 22031531 | 0 | 22031531 | 53 |  |
| 202602 | 3608 | 21980546 | 0 | 21980546 | 53 |  |
| 202603 | 3609 | 26564690 | 0 | 26564690 | 53 |  |
| 202604 | 3624 | 25367349 | 0 | 25367349 | 53 |  |
| 202605 | 3542 | 25811386 | 0 | 25811386 | 54 |  |
| 202606 | 3433 | 25155800 | 0 | 25155800 | 55 |  |
| 202607 | 2731 | 23635893 | 0 | 23635893 | 54 | municípios com produção < 90% da mediana do conjunto (3608) |

### generalistas

| Mês | Municípios com produção | Qtd. municípios | Qtd. ignorados | Total TabNet | Subgrupos | Sinal |
|---|---:|---:|---:|---:|---:|---|
| 202509 | 4742 | 45706046 | 0 | 45706046 | 50 |  |
| 202510 | 4744 | 46752443 | 0 | 46752443 | 51 |  |
| 202511 | 4735 | 43605373 | 0 | 43605373 | 50 |  |
| 202512 | 4728 | 41346570 | 0 | 41346570 | 51 |  |
| 202601 | 4712 | 42706406 | 0 | 42706406 | 50 |  |
| 202602 | 4697 | 41381499 | 0 | 41381499 | 51 |  |
| 202603 | 4654 | 47897967 | 0 | 47897967 | 51 |  |
| 202604 | 4629 | 45492431 | 0 | 45492431 | 50 |  |
| 202605 | 4519 | 45550429 | 0 | 45550429 | 51 |  |
| 202606 | 4273 | 43167904 | 0 | 43167904 | 50 |  |
| 202607 | 3380 | 36940483 | 0 | 36940483 | 52 | municípios com produção < 90% da mediana do conjunto (4697) |

### mfc_225130

| Mês | Municípios com produção | Qtd. municípios | Qtd. ignorados | Total TabNet | Subgrupos | Sinal |
|---|---:|---:|---:|---:|---:|---|
| 202509 | 54 | 83257 | 0 | 83257 | 11 | municípios com produção < 90% da mediana do conjunto (67) |
| 202510 | 60 | 95384 | 0 | 95384 | 15 | municípios com produção < 90% da mediana do conjunto (67) |
| 202511 | 64 | 75921 | 0 | 75921 | 15 | quantidade < 80% da mediana do conjunto (95384) |
| 202512 | 61 | 65146 | 0 | 65146 | 14 | quantidade < 80% da mediana do conjunto (95384) |
| 202601 | 67 | 78524 | 0 | 78524 | 12 |  |
| 202602 | 71 | 80462 | 0 | 80462 | 15 |  |
| 202603 | 72 | 100443 | 0 | 100443 | 13 |  |
| 202604 | 71 | 110651 | 0 | 110651 | 14 |  |
| 202605 | 74 | 117689 | 0 | 117689 | 15 |  |
| 202606 | 72 | 131208 | 0 | 131208 | 15 |  |
| 202607 | 49 | 122551 | 0 | 122551 | 16 | municípios com produção < 90% da mediana do conjunto (67) |

### todos_profissionais

| Mês | Municípios com produção | Qtd. municípios | Qtd. ignorados | Total TabNet | Subgrupos | Sinal |
|---|---:|---:|---:|---:|---:|---|
| 202509 | 5444 | 464760234 | 0 | 464760234 | 60 |  |
| 202510 | 5434 | 467686322 | 0 | 467686322 | 62 |  |
| 202511 | 5418 | 431470458 | 0 | 431470458 | 62 |  |
| 202512 | 5393 | 416332726 | 0 | 416332726 | 60 |  |
| 202601 | 5373 | 425094030 | 0 | 425094030 | 61 |  |
| 202602 | 5358 | 412091456 | 0 | 412091456 | 60 |  |
| 202603 | 5308 | 471033987 | 0 | 471033987 | 60 |  |
| 202604 | 5256 | 453115486 | 0 | 453115486 | 61 |  |
| 202605 | 5159 | 455653614 | 0 | 455653614 | 62 |  |
| 202606 | 4884 | 441589426 | 0 | 441589426 | 63 |  |
| 202607 | 3973 | 412423433 | 0 | 412423433 | 62 | municípios com produção < 90% da mediana do conjunto (5358) |

## Completude do CBO (todos os profissionais)

Produção sem CBO na tabela = total sem filtro − soma das linhas da consulta por CBO.

| Mês | Total | Soma por CBO | Sem CBO na tabela | Fração sem CBO |
|---|---:|---:|---:|---:|
| 202509 | 464760234 | 464259634 | 500600 | 0.001077 |
| 202510 | 467686322 | 466950214 | 736108 | 0.001574 |
| 202511 | 431470458 | 430929593 | 540865 | 0.001254 |
| 202512 | 416332726 | 415611539 | 721187 | 0.001732 |
| 202601 | 425094030 | 424107986 | 986044 | 0.002320 |
| 202602 | 412091456 | 411623073 | 468383 | 0.001137 |
| 202603 | 471033987 | 470450496 | 583491 | 0.001239 |
| 202604 | 453115486 | 452222838 | 892648 | 0.001970 |
| 202605 | 455653614 | 454947400 | 706214 | 0.001550 |
| 202606 | 441589426 | 439965292 | 1624134 | 0.003678 |
| 202607 | 412423433 | 411875713 | 547720 | 0.001328 |

## Subgrupos ao longo do tempo

Meses em que o subgrupo é coluna da resposta (o TabNet omite coluna sem registro sob o filtro). O grupo 09 (Ofertas de Cuidados Integrados, OCI) fica fora de consultas (0301), exames (02) e cirurgias (04) na definição do protocolo 47.

| Subgrupo | Rótulo | Primeiro mês (todos) | Último mês (todos) | Meses (todos) | Meses (alvo_pmme) | Qtd. total (todos) | Qtd. total (alvo_pmme) |
|---|---|---|---|---:|---:|---:|---:|
| 0101 | Acoes coletivas/individuais em saude | 202509 | 202607 | 11 | 11 | 193639095 | 856905 |
| 0102 | Vigilancia em saude | 202509 | 202607 | 11 | 11 | 17611807 | 252 |
| 0201 | Coleta de material | 202509 | 202607 | 11 | 11 | 46658185 | 932029 |
| 0202 | Diagnostico em laboratorio clinico | 202509 | 202607 | 11 | 11 | 945601085 | 6540614 |
| 0203 | Diagnostico por anatomia patologica e citopatologia | 202509 | 202607 | 11 | 11 | 11915190 | 7391724 |
| 0204 | Diagnostico por radiologia | 202509 | 202607 | 11 | 11 | 70331811 | 40666390 |
| 0205 | Diagnostico por ultrasonografia | 202509 | 202607 | 11 | 11 | 26421451 | 21892911 |
| 0206 | Diagnostico por tomografia | 202509 | 202607 | 11 | 11 | 12827116 | 12744082 |
| 0207 | Diagnostico por ressonancia magnetica | 202509 | 202607 | 11 | 11 | 2756024 | 2756024 |
| 0208 | Diagnostico por medicina nuclear in vivo | 202509 | 202607 | 11 | 0 | 512785 | 0 |
| 0209 | Diagnostico por endoscopia | 202509 | 202607 | 11 | 11 | 2706101 | 2519772 |
| 0210 | Diagnostico por radiologia intervencionista | 202509 | 202607 | 11 | 11 | 70880 | 44056 |
| 0211 | Metodos diagnosticos em especialidades | 202509 | 202607 | 11 | 11 | 70314985 | 10437373 |
| 0212 | Diagnostico e procedimentos especiais em hemoterapia | 202509 | 202607 | 11 | 11 | 17706781 | 79946 |
| 0213 | Diagnostico em vigilancia epidemiologica e ambiental | 202509 | 202607 | 11 | 11 | 1979716 | 527 |
| 0214 | Diagnostico por teste rapido | 202509 | 202607 | 11 | 11 | 55664382 | 176167 |
| 0301 | Consultas / Atendimentos / Acompanhamentos | 202509 | 202607 | 11 | 11 | 1471174182 | 48849559 |
| 0302 | Fisioterapia | 202509 | 202607 | 11 | 0 | 48743114 | 0 |
| 0303 | Tratamentos clinicos (outras especialidades) | 202509 | 202607 | 11 | 11 | 5915017 | 86395 |
| 0304 | Tratamento em oncologia | 202509 | 202607 | 11 | 11 | 4676075 | 4156461 |
| 0305 | Tratamento em nefrologia | 202509 | 202607 | 11 | 3 | 17731997 | 5 |
| 0306 | Hemoterapia | 202509 | 202607 | 11 | 11 | 7069822 | 28669 |
| 0307 | Tratamentos odontologicos | 202509 | 202607 | 11 | 11 | 23410283 | 145 |
| 0308 | Tratamento de lesoes, envenenamentos e outros, decorrentes de causas externas | 202510 | 202607 | 5 | 0 | 30 | 0 |
| 0309 | Terapias especializadas | 202509 | 202607 | 11 | 11 | 4299495 | 21833 |
| 0310 | Parto e nascimento | 202509 | 202607 | 11 | 11 | 9391 | 7070 |
| 0311 | Cuidados paliativos | 202509 | 202607 | 11 | 4 | 10342 | 87 |
| 0401 | Pequenas cirurgias e cirurgias de pele, tecido subcutaneo e mucosa | 202509 | 202607 | 11 | 11 | 12257575 | 1827065 |
| 0403 | Cirurgia do sistema nervoso central e periferico | 202509 | 202607 | 11 | 11 | 55027 | 795 |
| 0404 | Cirurgia das vias aereas superiores, da face, da cabeca e do pescoco | 202509 | 202607 | 11 | 11 | 642941 | 256157 |
| 0405 | Cirurgia do aparelho da visao | 202509 | 202607 | 11 | 11 | 2376703 | 4585 |
| 0406 | Cirurgia do aparelho circulatorio | 202509 | 202607 | 11 | 11 | 255970 | 38255 |
| 0407 | Cirurgia do aparelho digestivo, orgaos anexos e parede abdominal | 202509 | 202607 | 11 | 11 | 204728 | 182498 |
| 0408 | Cirurgia do sistema osteomuscular | 202509 | 202607 | 11 | 11 | 172804 | 3498 |
| 0409 | Cirurgia do aparelho geniturinario | 202509 | 202607 | 11 | 11 | 103393 | 48031 |
| 0410 | Cirurgia de mama | 202509 | 202607 | 11 | 11 | 3422 | 2655 |
| 0411 | Cirurgia obstetrica | 202509 | 202607 | 11 | 11 | 3381 | 2797 |
| 0412 | Cirurgia toracica | 202509 | 202607 | 11 | 11 | 7927 | 3443 |
| 0413 | Cirurgia reparadora | 202509 | 202607 | 11 | 11 | 117828 | 6943 |
| 0414 | Bucomaxilofacial | 202509 | 202607 | 11 | 11 | 5163342 | 202 |
| 0415 | Outras cirurgias | 202509 | 202607 | 11 | 11 | 274472 | 27853 |
| 0416 | Cirurgia em oncologia | 202510 | 202606 | 5 | 4 | 9 | 7 |
| 0417 | Anestesiologia | 202509 | 202607 | 11 | 11 | 1106608 | 800258 |
| 0418 | Cirurgia em nefrologia | 202509 | 202607 | 11 | 11 | 151750 | 6551 |
| 0501 | Coleta e exames para fins de doacao de orgaos, tecidos e celulas e de transplante | 202509 | 202607 | 11 | 11 | 1102815 | 28075 |
| 0503 | Acoes relacionadas a doacao de orgaos e tecidos para transplante | 202509 | 202607 | 11 | 11 | 33373 | 44 |
| 0504 | Processamento de tecidos para transplante | 202509 | 202607 | 11 | 0 | 58957 | 0 |
| 0505 | Transplante de orgaos, tecidos e celulas | 202509 | 202607 | 11 | 0 | 5225 | 0 |
| 0506 | Acompanhamento e intercorrencias no pre e pos-transplante | 202509 | 202607 | 11 | 11 | 428266 | 64917 |
| 0603 | Medicamentos de ambito hospitalar e urgencia | 202509 | 202607 | 11 | 0 | 1205 | 0 |
| 0604 | Componente Especializado da Assitencia Farmaceutica | 202509 | 202607 | 11 | 11 | 1673279366 | 1905 |
| 0701 | Orteses, proteses e materiais especiais nao relacionados ao ato cirurgico | 202509 | 202607 | 11 | 11 | 9828418 | 619382 |
| 0702 | Orteses, proteses e materiais especiais relacionados ao ato cirurgico | 202509 | 202607 | 11 | 11 | 291164 | 3380 |
| 0801 | Acoes relacionadas ao estabelecimento | 202509 | 202607 | 11 | 11 | 137279 | 2525 |
| 0802 | Acoes relacionadas ao atendimento | 202605 | 202607 | 3 | 3 | 1954 | 1954 |
| 0803 | Autorizacao / Regulacao | 202509 | 202607 | 11 | 11 | 80705569 | 3516723 |
| 0804 | Telessaude | 202509 | 202607 | 11 | 11 | 763949 | 579734 |
| 0901 | Atenção em Oncologia | 202509 | 202607 | 11 | 11 | 113343 | 106087 |
| 0902 | Atenção em Cardiologia | 202509 | 202607 | 11 | 11 | 433051 | 417092 |
| 0903 | Atenção em Ortopedia | 202509 | 202607 | 11 | 11 | 224138 | 7962 |
| 0904 | Atenção em Otorrinolaringologia | 202509 | 202607 | 11 | 11 | 63172 | 62021 |
| 0905 | Atenção em Oftalmologia | 202509 | 202607 | 11 | 0 | 1069185 | 0 |
| 0906 | Atenção em Saúde Mulher | 202509 | 202607 | 11 | 11 | 55721 | 54386 |

## Safra v2 frente à v1 (adendo §12.1 do protocolo 47)

Consultas da v2 entre 2026-10-19T21:09:20+00:00 e 2026-10-19T21:15:49+00:00 (UTC); as da v1 nesses meses entre 2026-10-19T12:52:14+00:00 e 2026-10-19T12:58:16+00:00.

Células comparadas: 14250618; diferentes: 0. Meses com revisão: nenhum.

| Mês | Conjunto | Células | Diferentes | Municípios com diferença | Qtd v1 | Qtd v2 | Diferença | Relativa |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 202509 | alvo_pmme | 295263 | 0 | 0 | 16424146 | 16424146 | 0 | 0.0000% |
| 202509 | especialistas_nao_alvo | 295263 | 0 | 0 | 27825715 | 27825715 | 0 | 0.0000% |
| 202509 | generalistas | 278550 | 0 | 0 | 45706046 | 45706046 | 0 | 0.0000% |
| 202509 | mfc_225130 | 61281 | 0 | 0 | 83257 | 83257 | 0 | 0.0000% |
| 202509 | todos_profissionais | 334260 | 0 | 0 | 464760234 | 464760234 | 0 | 0.0000% |
| 202510 | alvo_pmme | 295263 | 0 | 0 | 16373455 | 16373455 | 0 | 0.0000% |
| 202510 | especialistas_nao_alvo | 295263 | 0 | 0 | 28668640 | 28668640 | 0 | 0.0000% |
| 202510 | generalistas | 284121 | 0 | 0 | 46752443 | 46752443 | 0 | 0.0000% |
| 202510 | mfc_225130 | 83565 | 0 | 0 | 95384 | 95384 | 0 | 0.0000% |
| 202510 | todos_profissionais | 345402 | 0 | 0 | 467686322 | 467686322 | 0 | 0.0000% |
| 202511 | alvo_pmme | 300834 | 0 | 0 | 15165835 | 15165835 | 0 | 0.0000% |
| 202511 | especialistas_nao_alvo | 295263 | 0 | 0 | 25483566 | 25483566 | 0 | 0.0000% |
| 202511 | generalistas | 278550 | 0 | 0 | 43605373 | 43605373 | 0 | 0.0000% |
| 202511 | mfc_225130 | 83565 | 0 | 0 | 75921 | 75921 | 0 | 0.0000% |
| 202511 | todos_profissionais | 345402 | 0 | 0 | 431470458 | 431470458 | 0 | 0.0000% |
| 202512 | alvo_pmme | 289692 | 0 | 0 | 14388729 | 14388729 | 0 | 0.0000% |
| 202512 | especialistas_nao_alvo | 295263 | 0 | 0 | 23102483 | 23102483 | 0 | 0.0000% |
| 202512 | generalistas | 284121 | 0 | 0 | 41346570 | 41346570 | 0 | 0.0000% |
| 202512 | mfc_225130 | 77994 | 0 | 0 | 65146 | 65146 | 0 | 0.0000% |
| 202512 | todos_profissionais | 334260 | 0 | 0 | 416332726 | 416332726 | 0 | 0.0000% |
| 202601 | alvo_pmme | 295263 | 0 | 0 | 14209387 | 14209387 | 0 | 0.0000% |
| 202601 | especialistas_nao_alvo | 295263 | 0 | 0 | 22031531 | 22031531 | 0 | 0.0000% |
| 202601 | generalistas | 278550 | 0 | 0 | 42706406 | 42706406 | 0 | 0.0000% |
| 202601 | mfc_225130 | 66852 | 0 | 0 | 78524 | 78524 | 0 | 0.0000% |
| 202601 | todos_profissionais | 339831 | 0 | 0 | 425094030 | 425094030 | 0 | 0.0000% |
| 202602 | alvo_pmme | 289692 | 0 | 0 | 14064864 | 14064864 | 0 | 0.0000% |
| 202602 | especialistas_nao_alvo | 295263 | 0 | 0 | 21980546 | 21980546 | 0 | 0.0000% |
| 202602 | generalistas | 284121 | 0 | 0 | 41381499 | 41381499 | 0 | 0.0000% |
| 202602 | mfc_225130 | 83565 | 0 | 0 | 80462 | 80462 | 0 | 0.0000% |
| 202602 | todos_profissionais | 334260 | 0 | 0 | 412091456 | 412091456 | 0 | 0.0000% |
| 202603 | alvo_pmme | 295263 | 0 | 0 | 16485856 | 16485856 | 0 | 0.0000% |
| 202603 | especialistas_nao_alvo | 295263 | 0 | 0 | 26564690 | 26564690 | 0 | 0.0000% |
| 202603 | generalistas | 284121 | 0 | 0 | 47897967 | 47897967 | 0 | 0.0000% |
| 202603 | mfc_225130 | 72423 | 0 | 0 | 100443 | 100443 | 0 | 0.0000% |
| 202603 | todos_profissionais | 334260 | 0 | 0 | 471033987 | 471033987 | 0 | 0.0000% |
| 202604 | alvo_pmme | 295263 | 0 | 0 | 15822046 | 15822046 | 0 | 0.0000% |
| 202604 | especialistas_nao_alvo | 295263 | 0 | 0 | 25367349 | 25367349 | 0 | 0.0000% |
| 202604 | generalistas | 278550 | 0 | 0 | 45492431 | 45492431 | 0 | 0.0000% |
| 202604 | mfc_225130 | 77994 | 0 | 0 | 110651 | 110651 | 0 | 0.0000% |
| 202604 | todos_profissionais | 339831 | 0 | 0 | 453115486 | 453115486 | 0 | 0.0000% |
| 202605 | alvo_pmme | 306405 | 0 | 0 | 15747488 | 15747488 | 0 | 0.0000% |
| 202605 | especialistas_nao_alvo | 300834 | 0 | 0 | 25811386 | 25811386 | 0 | 0.0000% |
| 202605 | generalistas | 284121 | 0 | 0 | 45550429 | 45550429 | 0 | 0.0000% |
| 202605 | mfc_225130 | 83565 | 0 | 0 | 117689 | 117689 | 0 | 0.0000% |
| 202605 | todos_profissionais | 345402 | 0 | 0 | 455653614 | 455653614 | 0 | 0.0000% |
| 202606 | alvo_pmme | 300834 | 0 | 0 | 16010626 | 16010626 | 0 | 0.0000% |
| 202606 | especialistas_nao_alvo | 306405 | 0 | 0 | 25155800 | 25155800 | 0 | 0.0000% |
| 202606 | generalistas | 278550 | 0 | 0 | 43167904 | 43167904 | 0 | 0.0000% |
| 202606 | mfc_225130 | 83565 | 0 | 0 | 131208 | 131208 | 0 | 0.0000% |
| 202606 | todos_profissionais | 350973 | 0 | 0 | 441589426 | 441589426 | 0 | 0.0000% |
| 202607 | alvo_pmme | 300834 | 0 | 0 | 14174344 | 14174344 | 0 | 0.0000% |
| 202607 | especialistas_nao_alvo | 300834 | 0 | 0 | 23635893 | 23635893 | 0 | 0.0000% |
| 202607 | generalistas | 289692 | 0 | 0 | 36940483 | 36940483 | 0 | 0.0000% |
| 202607 | mfc_225130 | 89136 | 0 | 0 | 122551 | 122551 | 0 | 0.0000% |
| 202607 | todos_profissionais | 345402 | 0 | 0 | 412423433 | 412423433 | 0 | 0.0000% |
