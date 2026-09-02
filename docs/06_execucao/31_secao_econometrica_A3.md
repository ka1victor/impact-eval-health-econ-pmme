# Seção econométrica congelada — A3 (02/09/2026)

> Registro: `output/tema_trabalho/registro_pre_analise_atracao.json`
> Potência: `output/tema_trabalho/potencia_atracao.json`
> Tipologia: A2 `APROVADO_4_ESTRATOS` strict — 540/540 municípios (25/101/238/176); quadro Ch1 368 mun. (18/72/203/75) — REGIC 2018 + RM/RIDE 2022 strict

**Pergunta.** Quais características territoriais e das vagas estão associadas ao
preenchimento administrativo (alguma confirmação/homologação na célula) e,
condicionalmente, à persistência da oferta local?

**População.** 1.295 células CNES–curso do quadro Ch1 (368 municípios) como
primária; 3.057 células do funil A1 como estendida.

**Outcome primário.** Binário por célula: `1[n_confirmacoes_ch1>0 ou n_homologacoes_ch1>0]`.
Taxa por vaga permanece proibida (A1).

**Unidade de inferência.** Município (cluster-robusto; FE de curso e UF).

**Modelos.** LPM (primário) e logit/AME (alternativo); binomial/logit por célula;
Poisson/NB apenas descritivo para contagens.

**Covariadas.** Estrato A2, IVS 2010 canônico (+ subíndices), log(pop 2010),
região de saúde, estoque pré 202407–202506, faixa anunciada, curso, UF, chamada.

**Potência.** Global MDE 80% ≈ 3.8% (p=0.30)
a 4.1% (p=0.50) com DEFF=1.126 (m≈3.52, ICC=0.05);
por estrato (quadro Ch1, DEFF=max(1,1+(m-1)*ICC)): capital 73/18 m≈4.06 MDE≈16.1% (p30, DEFF 1.153),
metropolitano 265/72 MDE≈8.4%,
interior_proximo 811/203 MDE≈4.8%,
interior_remoto 146/75 MDE≈10.9%.
Mínima relevante 10pp (sens. 5pp); MDE>10pp indica poder limitado para nulidade.

**Linguagem.** Associativa apenas; sem efeito causal do PMM-E/bolsa/IVS.
