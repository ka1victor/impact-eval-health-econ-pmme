# Seção econométrica congelada — A3 (02/09/2026)

> Registro: `output/tema_trabalho/registro_pre_analise_atracao.json`
> Potência: `output/tema_trabalho/potencia_atracao.json`
> Tipologia: A2 `APROVADO_4_ESTRATOS` — 540/540 municípios

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
a 4.1% (p=0.50) com DEFF=1.126;
por estrato: remoto ≈ 10.6%,
metropolitano ≈ 7.9%. Mínima
relevante 10pp (sens. 5pp).

**Linguagem.** Associativa apenas; sem efeito causal do PMM-E/bolsa/IVS.
