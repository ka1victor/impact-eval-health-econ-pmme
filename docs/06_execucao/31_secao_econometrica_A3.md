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

**Potência.** O antigo valor global de 3.8%
é mantido apenas como benchmark de precisão de uma proporção e **não** como
MDE dos coeficientes territoriais. Para os contrastes efetivamente estimados
contra interior_remoto (referência), os MDEs aproximados a 80% (p=0,30; DEFF por estrato)
são: capital 19.5%,
metropolitano 13.7% e
interior_proximo_polo 11.9%.
São benchmarks analíticos; não substituem simulação com a matriz completa do
modelo. A mínima diferença relevante permanece 10 p.p. (sensibilidade 5 p.p.).

**Linguagem.** Associativa apenas; sem efeito causal do PMM-E/bolsa/IVS.
