# A05 — Aquisição e inspeção do CNES mensal

## Pré-requisitos

Leia `AGENTS.md`, `CLAUDE.md`, `prompts/aquisicao_dados/README.md`, a auditoria
02 e `scripts/03_planejar_aquisicao_cnes.py`. Trabalhe em worktree isolado e
confirme espaço em disco antes de qualquer download grande.

## Missão

Adquirir do catálogo oficial as competências mensais do CNES necessárias para
medir vínculos, FTE cadastral, vínculos anteriores/simultâneos e infraestrutura
pré-tratamento. Esta frente valida esquema e cobertura; não atribui vínculos ao
PMM-E sem ponte administrativa.

## Janela de aquisição

Use duas etapas:

1. **piloto de esquema:** junho/2024, junho/2025 e a competência oficial mais
   recente, para verificar formato, tamanho, tabelas e chaves;
2. **painel integral:** junho/2024 até a competência mais recente disponível,
   somente depois de o piloto passar e de confirmar espaço suficiente.

Junho/2024 fornece 12 meses de histórico antes da primeira oferta pública de
2025. Se a competência mais recente mudar durante a execução, registre a data do
catálogo e congele o fim da aquisição; não misture releases publicados depois do
corte sem nova versão do manifesto.

## Módulos e campos mínimos

- estabelecimento: CNES, município/IBGE, natureza, tipo e situação cadastral;
- profissional–vínculo: identificador longitudinal disponível, CNES, CBO,
  vínculo, competência e cargas horárias ambulatorial, hospitalar e outras;
- infraestrutura prévia: serviços, habilitações, leitos e equipamentos;
- dicionários, layouts e documentação de cada competência.

Identifique os nomes reais das tabelas no ZIP antes de programar a extração.
CNES mede cadastro e carga declarada, não frequência nem horas efetivamente
trabalhadas.

## Entregáveis exclusivos

- ZIPs brutos imutáveis em `data/raw/cnes/`, sem versionar arquivos grandes no
  Git;
- script idempotente em `scripts/aquisicao/a05_adquirir_cnes.py`;
- `output/aquisicao/a05_manifesto_cnes.json`, com hash de cada ZIP;
- `output/aquisicao/a05_dicionario_tabelas_cnes.json`;
- `docs/auditorias/aquisicao/A05_cnes_mensal.md`.

O script deve oferecer modo `--plan`, modo piloto e modo integral com confirmação
explícita. Deve baixar para arquivo temporário, validar assinatura/tamanho e só
então mover para o nome final. Não sobrescreva ZIP existente e não descompacte
tudo permanentemente se uma leitura seletiva resolver.

Como os ZIPs não entram no commit, entregue também ao coordenador o caminho
absoluto da worktree que os contém. A worktree não pode ser removida antes de o
coordenador transferir os arquivos para o workspace principal ou repetir ali a
aquisição e confirmar todos os hashes.

## Validações e critério de aceite

- continuidade das competências e hashes completos;
- estabilidade/mudanças de esquema;
- unicidade e cobertura das chaves relevantes;
- presença dos CNES publicados nas vagas, sem interpretar ausência como zero;
- viabilidade de construir FTE e baseline de infraestrutura;
- diagnóstico explícito sobre a ponte PMM-E–CNES ainda ausente.

Se espaço, rede ou servidor impedirem o painel integral, preserve o piloto e um
manifesto completo de URLs/status; não produza arquivos vazios como substitutos.
Não altere documentação compartilhada ou `run_all.py`. Valide, faça commit
próprio e informe hash e bloqueios; não faça push ou merge.
