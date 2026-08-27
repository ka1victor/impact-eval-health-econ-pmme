# Prompt 04 — Painel de vagas e cobertura sustentada

Execute somente se `docs/07_protocolo_empirico_congelado.md` autorizar o prosseguimento e a Base A estiver disponível.

Leia `AGENTS.md`, `CLAUDE.md`, o roadmap, o protocolo e os relatórios de auditoria.

## Missão

Implementar um pipeline determinístico que construa a unidade vaga–especialidade–chamamento e sua trajetória temporal. Não estime impacto causal.

Calcule conforme o protocolo:

- data de oferta;
- candidatura e convocação;
- aceite;
- entrada efetiva;
- saída e afastamentos;
- spells de ocupação;
- cobertura na janela congelada;
- preenchimento em 30/60/90 dias;
- tempo até entrada;
- dias vagos posteriores;
- rotatividade;
- censura.

Trate explicitamente:

- vagas com múltiplas posições;
- reabertura;
- substituições;
- transferências;
- eventos simultâneos;
- datas inconsistentes;
- observações sem seguimento completo.

## Requisitos de implementação

- Nunca altere dados brutos.
- Grave transformações somente em `output/`.
- Use caminhos relativos à raiz.
- Gere dicionário, fluxo de exclusões, hashes e validações automatizadas.
- Verifique que cobertura está entre 0 e 1 e que a cronologia é possível.
- Atualize `run_all.py` somente com etapas reproduzíveis a partir dos insumos documentados.

## Limites

- Não estimar efeito causal.
- Não preencher lacunas com simulação.
- Não iniciar WP3, WP4 ou WP5.
- Não fazer push ou merge.

Ao final, execute o pipeline, reconcilie contagens, faça commit próprio e informe hash, outputs e limitações.
