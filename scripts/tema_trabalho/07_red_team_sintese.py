"""A6 — Red team, matriz de evidências e síntese coerente das etapas A1–A5."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "tema_trabalho"
AUD = ROOT / "docs" / "auditorias"
EXEC = ROOT / "docs" / "06_execucao"

A4 = OUT / "A4_estimativas_atracao.json"
A5 = OUT / "A5_estimativas_provimento.json"
REDTEAM = AUD / "09_red_team_atracao_provimento.md"
MATRIX_DOC_CSV = AUD / "09_matriz_afirmacao_evidencia_limite.csv"
MATRIX_OUT_CSV = OUT / "A6_matriz_afirmacao_evidencia_limite.csv"
MATRIX_MD = AUD / "09_matriz_afirmacao_evidencia_limite.md"
SYNTHESIS = EXEC / "32_sintese_A6_resumo_intro_metodos_conclusao.md"
MANIFEST = OUT / "A6_manifesto_reproducao.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_text(path: Path, value: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(value, encoding="utf-8")
    tmp.replace(path)


def pct(value: float) -> str:
    return f"{100 * value:.1f}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    AUD.mkdir(parents=True, exist_ok=True)
    EXEC.mkdir(parents=True, exist_ok=True)
    a4 = json.loads(A4.read_text(encoding="utf-8"))
    a5 = json.loads(A5.read_text(encoding="utf-8"))
    m4 = a4["modelos"]
    m5 = a5["modelos"]

    metro = m4["primario_LPM_minimal"]["coef_estrato"]["estrato_metropolitano"]
    metro_full = m4["sensibilidade_full"]["coef_estrato_full"]["estrato_metropolitano"]
    confirm = m4["robustez_estagios_funil"]["alguma_confirmacao"]["coef_estrato"]["estrato_metropolitano"]
    homolog = m4["robustez_estagios_funil"]["alguma_homologacao"]["coef_estrato"]["estrato_metropolitano"]
    collapsed = m4["robustez_municipio_curso"]["coef_estrato"]["estrato_metropolitano"]
    event = m5["principal_dinamico_confirmatorio"]
    expanded = m5["sensibilidade_dinamica_ampliada"]
    dist0 = m5["distribuicao_delta_confirmatoria"]["0"]
    dist1 = m5["distribuicao_delta_confirmatoria"]["1"]
    date = dt.date.today().isoformat()

    redteam = f"""# A6 — Red team da evidência empírica

> Data: {date}  
> Escopo máximo: evidência associativa de implementação e evolução da oferta médica cadastrada.  
> Resultado principal: atração administrativa (A4). Resultado secundário: dinâmica agregada do CNES (A5).

## Método de refutação

Cada afirmação foi atacada por mudança de denominador, estágio do funil, unidade de observação, amostra CBO, período de referência, controles, influência e linguagem. “Passar” significa apenas sobreviver a esses testes; não transforma associação em efeito causal.

## Checklist e vereditos

### 1. Denominador e versionamento

**Refutação tentada:** usar 678 vagas imediatas como denominador e interpretar confirmações em reserva como preenchimento de vaga imediata. Há células com eventos acima da capacidade publicada e a chamada 2 não oferece quantidade imediata comparável.  
**Veredito:** usar a célula CNES–curso e o indicador de alguma confirmação ou homologação. Taxa por vaga fica bloqueada.

### 2. População territorial definida antes do resultado

**Refutação tentada:** redefinir interior depois de observar os coeficientes.  
**Veredito:** mantida a tipologia REGIC 2018 + RM/RIDE 2022 em quatro estratos, congelada antes da estimação: capital, metropolitano, interior próximo e interior remoto.

### 3. Seleção de municípios, cursos e estabelecimentos

**Refutação tentada:** misturar cursos com ponte CBO sobreposta e atribuir a mudança a uma especialidade específica.  
**Veredito:** A4 cobre 1.295 células em 368 municípios; A5 principal restringe-se a 587 células município–curso de dez cursos com CBO unívoco, em 295 municípios. A amostra ampliada é apenas sensibilidade.

### 4. Inferência municipal e concentração

**Refutação tentada:** usar erros independentes por célula e ignorar exposição comum dentro do município.  
**Veredito:** erros agrupados por município em todos os modelos principais. Leave-one-out (LOO) por UF, curso e município e diagnóstico de influência permanecem obrigatórios.

### 5. Confirmação, homologação, entrada e permanência

**Refutação tentada:** chamar confirmação de entrada física ou presença cadastral de retenção.  
**Veredito:** os estágios são separados. Em A4, o contraste metropolitano é {pct(confirm)} pp para confirmação e {pct(homolog)} pp para homologação. Em A5, “entrada” é um novo vínculo no mês após washout de seis meses, não um fluxo acumulado semestral.

### 6. IVS e faixa de bolsa

**Refutação tentada:** interpretar IVS, faixa e valor anunciado como fontes independentes de variação.  
**Veredito:** a grade administrativa é colinear e a regra não foi reproduzida para 177/368 municípios. IVS 2010 continua a running variable canônica, mas o RDD foi encerrado no portão R1.

### 7. CNES e retenção individual

**Refutação tentada:** usar estoque municipal do CBO para afirmar permanência do bolsista.  
**Veredito:** CNES mede oferta cadastrada agregada. Sem ponte nominal validada, não identifica participação no PMM-E nem retenção individual.

### 8. RDD

**Refutação tentada:** forçar descontinuidade em IVS=0,4 apesar da falha na reconstrução da regra e do suporte discreto.  
**Veredito:** RDD encerrado em R1; nenhuma afirmação causal do adicional da bolsa.

### 9. SIH/SIA, fila, saúde e custo-benefício

**Refutação tentada:** extrapolar estoque cadastral para resolutividade, internações, fila ou retorno econômico.  
**Veredito:** sem SIH/SIA e sem portão de linkage/pagamentos, esses desfechos ficam fora do núcleo empírico atual.

## Ataques ao resultado principal (A4)

- O contraste metropolitano versus interior remoto é {pct(metro)} pp no LPM pré-especificado e {pct(metro_full)} pp no ajuste completo.
- Separar o funil preserva o sinal: {pct(confirm)} pp em confirmação e {pct(homolog)} pp em homologação.
- Colapsar múltiplos CNES para município–curso aumenta o contraste para {pct(collapsed)} pp; logo, o resultado não decorre do peso implícito de estabelecimentos múltiplos.
- Winsorizar covariadas e executar leave-one-out não inverte o gradiente. O resultado é robusto como associação territorial, não como efeito da bolsa.

## Ataques ao resultado secundário (A5)

- Setembro/2025 foi rejeitado como baseline porque já contém exposição física. A referência limpa é junho/2025 e o follow-up comum é março/2026.
- O estudo dinâmico usa efeitos fixos de célula, curso–mês e UF–mês, com cluster municipal. Em março/2026, a diferença associada à atração é {event['mar2026_beta']:.2f} (EP {event['mar2026_se']:.2f}; p={event['mar2026_p']:.3f}); o teste conjunto prévio tem p={event['pre_p']:.3f}.
- A sensibilidade ampliada produz {expanded['mar2026_beta']:.2f} (p={expanded['mar2026_p']:.3f}), mas mistura CBOs sobrepostos.
- A distribuição é assimétrica: sem atração, média {dist0['media']:.2f}, mediana {dist0['mediana']:.0f}, máximo {dist0['max']:.0f}; com atração, média {dist1['media']:.2f}, mediana {dist1['mediana']:.0f}, máximo {dist1['max']:.0f}. Winsorizar muda materialmente a precisão, portanto médias simples não bastam.
- O modelo de nível é dominado por diferenças basais e a validação preditiva fora da amostra é fraca. Ambos ficam como diagnósticos.

## Veredito geral

O núcleo útil é a desigualdade territorial na atração administrativa, robusta ao estágio do funil e à unidade analítica. A evolução do estoque cadastral após a oferta é compatível com uma diferença positiva modesta, mas vulnerável a caudas, composição e tempo de exposição heterogêneo. Não há base para reivindicar efeito causal, provimento atribuível ao programa ou retenção individual.

*Gerado por `scripts/tema_trabalho/07_red_team_sintese.py`.*
"""
    atomic_text(REDTEAM, redteam)

    matrix_rows = [
        ("Atração administrativa média de 30,3%", "393 de 1.295 células", "Célula não é vaga física", "prevalência administrativa observada"),
        (f"Metropolitano associado a +{pct(metro)} pp versus remoto", "LPM com FE curso e UF; cluster município", f"Ajuste completo: +{pct(metro_full)} pp", "associado a maior atração"),
        ("Resultado preservado em confirmação", f"Contraste metropolitano +{pct(confirm)} pp", "Confirmação não é entrada física", "associação no estágio de confirmação"),
        ("Resultado preservado em homologação", f"Contraste metropolitano +{pct(homolog)} pp", "Homologação não é exercício", "associação no estágio de homologação"),
        ("Resultado preservado ao colapsar CNES", f"Município–curso: +{pct(collapsed)} pp", "Muda o peso analítico", "robustez à unidade"),
        ("IVS/faixa não identificam efeito marginal", "Coeficientes conjuntos instáveis e R1 falhou", "Regra administrativa não reproduzida", "gradiente descritivo"),
        (f"Dinâmica CNES em março/2026: +{event['mar2026_beta']:.2f}", f"FE célula, curso–mês, UF–mês; p={event['mar2026_p']:.3f}", "Atração é resultado realizado; sem grupo causal", "associado a trajetória diferencial"),
        ("Pré-tendências não rejeitadas", f"Teste conjunto p={event['pre_p']:.3f}", "Não rejeitar não prova paralelismo", "diagnóstico favorável, não validação causal"),
        ("Distribuição da mudança é assimétrica", f"Medianas {dist0['mediana']:.0f} e {dist1['mediana']:.0f}; máximo com atração {dist1['max']:.0f}", "Cauda extrema influencia a média", "descrever média, mediana e caudas"),
        ("CNES não mede retenção individual", "Agregação município–curso", "Sem ponte nominal de bolsistas", "oferta médica cadastrada local"),
        ("RDD, SIH/SIA e custo-benefício fora do núcleo", "RDD encerrado em R1; bases/portões ausentes", "Sem identificação ou linkage", "não afirmar sem novo desenho"),
    ]
    columns = ["afirmacao", "evidencia", "limite", "linguagem_maxima"]
    matrix = pd.DataFrame(matrix_rows, columns=columns)
    for path in (MATRIX_DOC_CSV, MATRIX_OUT_CSV):
        tmp = path.with_suffix(path.suffix + ".tmp")
        matrix.to_csv(tmp, index=False)
        tmp.replace(path)
    md_table = "| Afirmação | Evidência | Limite | Linguagem máxima |\n|---|---|---|---|\n"
    for row in matrix.itertuples(index=False):
        md_table += "| " + " | ".join(str(v).replace("|", "/") for v in row) + " |\n"
    atomic_text(MATRIX_MD, f"# Matriz afirmação–evidência–limite (A6)\n\n> Data: {date}\n\n{md_table}")

    synthesis = f"""# Síntese empírica A6

> **Título recomendado:** Atração administrativa de médicos especialistas e gradientes territoriais: evidências de implementação do PMM-E.  
> **Nível de identificação:** associativo. RDD encerrado em R1; retenção individual não identificada.  
> **Hashes:** A4 `{sha256(A4)[:8]}`; A5 `{sha256(A5)[:8]}`.

## Resumo

Analisamos a implementação do primeiro ciclo do PMM-E em 1.295 células CNES–curso de 368 municípios. Alguma confirmação ou homologação ocorreu em 30,3% das células. Em modelo linear com efeitos fixos de curso e UF e erros agrupados por município, células metropolitanas tiveram probabilidade {pct(metro)} pontos percentuais maior que as do interior remoto; o contraste foi {pct(metro_full)} pontos no ajuste completo, {pct(confirm)} na confirmação, {pct(homolog)} na homologação e {pct(collapsed)} ao colapsar para município–curso. Como evidência secundária, um estudo dinâmico do CNES em 587 células de dez cursos com CBO unívoco encontrou diferença associada à atração de {event['mar2026_beta']:.2f} médico cadastrado em março/2026 (EP {event['mar2026_se']:.2f}), relativa a junho/2025. A distribuição é assimétrica e contém máximo 211 no grupo com atração. Os achados sustentam um gradiente territorial de implementação e uma trajetória cadastral diferencial modesta; não sustentam efeito causal da bolsa, provimento atribuível ao programa ou retenção individual.

## Introdução

O problema empiricamente identificável hoje não é o retorno causal de cada faixa de bolsa, mas onde a oferta administrativa atraiu ao menos uma confirmação ou homologação. IVS 2010 permanece a variável canônica do desenho previsto, porém faixa e IVS não fornecem variação independente, e a regra administrativa não foi reproduzida em 177 dos 368 municípios. Por isso o RDD foi encerrado no primeiro portão. A contribuição atual é medir desigualdades territoriais na implementação e documentar, separadamente, a evolução da oferta médica cadastrada no CNES.

## Métodos

A análise principal usa células CNES–curso da chamada 1, tipologia territorial REGIC/RM-RIDE congelada antes da estimação e LPM pré-especificado com efeitos fixos de curso e UF e cluster municipal; Logit, ajuste completo, estágios do funil, colapso município–curso, winsorização e leave-one-out são robustez. O benchmark global de 3,8 pp é precisão de uma proporção, não MDE do contraste territorial; para metropolitano versus interior remoto, o MDE prévio é 13,7 pp sob p=0,30.

A análise secundária usa 26 competências CNES e, como amostra principal, 587 células município–curso em 295 municípios. Junho/2025 é a última referência limpa antes da oferta; setembro/2025 já pode estar tratado. O estudo dinâmico absorve efeitos fixos de célula, curso–mês e UF–mês, com erros agrupados por município. Atração administrativa é um resultado realizado, não tratamento exógeno. Estoque e entradas referem-se a vínculos cadastrados; não identificam médicos do programa.

## Conclusão

O resultado publicável é um gradiente territorial de atração: municípios metropolitanos apresentam maior probabilidade de atração administrativa que o interior remoto, e o padrão resiste à separação entre confirmação e homologação e ao colapso da unidade. A dinâmica do CNES sugere diferença positiva posterior, com pré-tendências não rejeitadas, mas a cauda extrema, a composição e o tempo de exposição física heterogêneo limitam sua interpretação. Sem base para efeito causal do adicional da bolsa, retenção individual, resolutividade, fila, SIH/SIA ou custo-benefício, esses objetos exigem novos dados e novo protocolo antes de qualquer estimação.
"""
    atomic_text(SYNTHESIS, synthesis)

    key_files = [
        ROOT / "output/aquisicao/quadro_vagas_tratamento.parquet",
        OUT / "matriz_funil_ciclo1.parquet",
        OUT / "matriz_tipologia_territorial.parquet",
        OUT / "portao_denominador.json",
        OUT / "registro_pre_analise_atracao.json",
        OUT / "potencia_atracao.json",
        ROOT / "output/aquisicao/ponte_curso_cbo_oficial.json",
        ROOT / "output/painel_municipio_curso_mensal.parquet",
        A4,
        A5,
        OUT / "A5_manifesto_maturidade_censura.json",
        OUT / "A4_tabela_02_modelo_principal_LPM.csv",
        OUT / "A4_tabela_02c_confirmacao_homologacao.csv",
        OUT / "A4_tabela_02d_municipio_curso.csv",
        OUT / "A5_tabela_07_estudo_evento_atracao.csv",
        REDTEAM,
        MATRIX_OUT_CSV,
        SYNTHESIS,
    ]
    hashes = {
        path.relative_to(ROOT).as_posix(): {"sha256": sha256(path), "bytes": path.stat().st_size}
        for path in key_files if path.exists()
    }
    docs_hash = {
        path.relative_to(ROOT).as_posix(): sha256(path)[:8]
        for path in (REDTEAM, MATRIX_DOC_CSV, MATRIX_MD, SYNTHESIS)
    }
    commands = [
        ".venv\\Scripts\\python.exe scripts/tema_trabalho/02_reconciliar_funil_ciclo1.py",
        ".venv\\Scripts\\python.exe scripts/tema_trabalho/03_construir_tipologia_territorial.py",
        ".venv\\Scripts\\python.exe scripts/tema_trabalho/04_congelar_pre_analise.py",
        ".venv\\Scripts\\python.exe scripts/tema_trabalho/05_estimar_atracao.py",
        ".venv\\Scripts\\python.exe scripts/tema_trabalho/06_avaliar_provimento_cnes.py",
        ".venv\\Scripts\\python.exe scripts/tema_trabalho/07_red_team_sintese.py",
        ".venv\\Scripts\\python.exe -m unittest discover -s tests -q",
    ]
    manifest = {
        "protocolo": "A6_MANIFESTO_REPRODUCAO",
        "data_referencia": date,
        "gerador": "scripts/tema_trabalho/07_red_team_sintese.py",
        "fila": "A1->A6: núcleo associativo; upgrade causal bloqueado",
        "comandos_reproducao": commands,
        "versoes": {
            "python": sys.version,
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "statsmodels": statsmodels.__version__,
        },
        "hashes_entradas_e_artefatos": hashes,
        "docs_hash8": docs_hash,
        "portoes": {
            "A1_APROVADO_CELULA": "output/tema_trabalho/portao_denominador.json",
            "A2_APROVADO_4_ESTRATOS": "output/tema_trabalho/manifesto_tipologia_territorial.json",
            "A3_CONGELADO": "output/tema_trabalho/registro_pre_analise_atracao.json",
            "A4_ASSOCIATIVO": "output/tema_trabalho/A4_estimativas_atracao.json",
            "A5_DINAMICA_ASSOCIATIVA": "output/tema_trabalho/A5_estimativas_provimento.json",
            "R1_RDD_ENCERRADO": "output/rdd_bolsa/diagnostico_viabilidade_salario_ivs.json",
        },
        "limites_reafirmados": [
            "Sem taxa por vaga física",
            "Sem efeito causal da faixa ou do IVS",
            "Sem retenção individual no CNES agregado",
            "Sem SIH/SIA, fila, saúde ou custo-benefício sem novo portão",
            "A5 sensível a composição, caudas e tempo de exposição",
        ],
        "checklist_A6_passou": [
            "denominador_versionamento",
            "populacao_territorial_previa",
            "selecao_municipios_cursos_estabs",
            "inferencia_municipal_concentracao",
            "distincao_confirmacao_homologacao_entrada_permanencia",
            "ivs_faixa_nao_independentes",
            "cnes_nao_retencao",
            "rdd_encerrado_R1",
            "sem_sih_sia_fila",
        ],
        "entregaveis_A6": {
            "red_team": REDTEAM.relative_to(ROOT).as_posix(),
            "matriz_csv_docs": MATRIX_DOC_CSV.relative_to(ROOT).as_posix(),
            "matriz_csv_out": MATRIX_OUT_CSV.relative_to(ROOT).as_posix(),
            "matriz_md": MATRIX_MD.relative_to(ROOT).as_posix(),
            "sintese": SYNTHESIS.relative_to(ROOT).as_posix(),
            "manifesto": MANIFEST.relative_to(ROOT).as_posix(),
        },
    }
    atomic_text(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"[OK] A6 concluído: {len(matrix)} afirmações auditadas; manifesto {MANIFEST}")


if __name__ == "__main__":
    main()
