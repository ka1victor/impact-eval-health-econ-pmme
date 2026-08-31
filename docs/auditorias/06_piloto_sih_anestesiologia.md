# Auditoria do SIH pré-tratamento — Anestesiologia (C3-02B)

> **Execução:** 2026-08-31<br>
> **Status:** bloqueado por fonte oficial incompleta<br>
> **C3-03 clínico/SIH:** bloqueado; força de trabalho/CNES é independente

## Resultado

A execução tentou os **675 pares UF--competência** de 2024-06 a 2026-06.
Houve **673 sucessos**. O diretório oficial do SIH não contém
`RDAC2606.dbc` nem `RDRR2606.dbc`; a ausência foi confirmada por listagem do
[FTP DATASUS](ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados)
em 2026-08-31T03:59:06.687609+00:00. O cronograma previa disseminação aproximada de junho em
10/08/2026, mas o catálogo observado em 31/08/2026 ainda tinha só 25 UFs.

O manifesto `output/avaliacao_ciclo3/manifesto_arquivos_sih_pre.csv` tem uma
linha para cada um dos 675 pares, com 673 `SUCCESS` e duas falhas FTP 550.
Conforme o prompt, as duas ausências **não foram convertidas em zeros** e os
painéis corrigidos não foram construídos.

## Parte concluída

- as 25 competências mensais do SIGTAP foram historicizadas;
- o dicionário tem 42,358 linhas competência--procedimento do grupo 04;
- a classificação municipal continua reconciliada em 77 tratados puros, 247
  controles puros e um município imediata+reserva excluído;
- tráfego parcial da tentativa principal: 2244.15 MiB;
- o pico de disco não foi inferido: a medição morreu com o processo bloqueado e
  agora o código falha no pré-flight antes de repetir uma aquisição incompleta.

Os Parquets já existentes são produtos preliminares do C3-02 (24 UFs), não
produtos aprovados do C3-02B. Seus hashes ficam no manifesto apenas para impedir
que sejam confundidos com a correção.

## Portão

O portão clínico do C3-03 permanece bloqueado. O torneio de força de trabalho
foi executado separadamente, somente com CNES pré-T0. Próxima ação clínica:
verificar novamente o FTP e executar o C3-02B integral quando os dois arquivos
forem publicados. Nenhum outcome pós-tratamento foi consultado e nenhuma
estimação foi feita. C3-05 continua proibido até `202703` estar madura.
