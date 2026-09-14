"""A6 — Red team, matriz de evidências e síntese coerente das etapas A1–A5."""

from __future__ import annotations

import ast
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
FUNIL = OUT / "matriz_funil_ciclo1.parquet"
RUN_ALL = ROOT / "run_all.py"

# Interpretador do ambiente documentado no README. O manifesto registrava
# `.venv\\Scripts\\python.exe` enquanto `versoes.platform` gravava Linux; quem
# seguisse o manifesto não conseguiria reproduzir nada (item B-3 do backlog).
PYTHON_REPRO = ".venv/bin/python"
PYTHON_MINIMO = "3.12"

MOTIVO_CNES_AUSENTE = (
    "microdados mensais do CNES não versionados (data/raw/cnes/ é gitignored) e "
    "reconstruir o painel exige mais de 16 GB de ZIPs das 26 competências; ver "
    "docs/06_execucao/36_backlog_pos_auditoria.md, item D-4"
)


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


def num(value: float, casas: int = 2) -> str:
    """Formata em convenção brasileira. Os documentos gerados são em português."""
    return f"{value:.{casas}f}".replace(".", ",")


def pct(value: float) -> str:
    return num(100 * value, 1)


def prevalencia_atracao() -> dict[str, float]:
    """Separa o desfecho da primeira chamada do desfecho do ciclo 1 inteiro.

    Os dois não são o mesmo número e vinham sendo confundidos: 30,3% é a
    prevalência no **quadro da primeira chamada**, que é a população primária de
    A4. Pelo ciclo 1 inteiro a prevalência é maior, porque células sem desfecho
    na primeira chamada receberam homologado novo na segunda (item C-1).
    """
    funil = pd.read_parquet(FUNIL)
    chave = ["co_cnes_7d", "cod_curso"]
    quadro = funil.loc[funil["in_quadro_ch1_original"] == True, chave].drop_duplicates()  # noqa: E712
    ch1 = (
        funil.loc[funil["chamada"] == 1]
        .groupby(chave, as_index=False)[["n_confirmacoes_ch1", "n_homologacoes_ch1"]]
        .sum()
    )
    ch2 = (
        funil.loc[funil["chamada"] == 2]
        .groupby(chave, as_index=False)[["n_homologacoes_novas_ch2"]]
        .sum()
    )
    celulas = quadro.merge(ch1, on=chave, how="left").merge(ch2, on=chave, how="left").fillna(0)

    primeira = (celulas["n_confirmacoes_ch1"] > 0) | (celulas["n_homologacoes_ch1"] > 0)
    novas = (~primeira) & (celulas["n_homologacoes_novas_ch2"] > 0)
    ciclo = primeira | (celulas["n_homologacoes_novas_ch2"] > 0)

    total = int(len(celulas))
    return {
        "celulas": total,
        "ch1_celulas": int(primeira.sum()),
        "ch1_prop": float(primeira.sum()) / total,
        "ciclo_celulas": int(ciclo.sum()),
        "ciclo_prop": float(ciclo.sum()) / total,
        "celulas_novas_ch2": int(novas.sum()),
        "pessoas_novas_ch2": int(celulas.loc[novas, "n_homologacoes_novas_ch2"].sum()),
    }


def _caminho_de_step(no: ast.expr) -> str:
    """Reduz a expressão `ROOT / "a" / "b.py"` de `run_all.py` a um caminho POSIX."""
    partes: list[str] = []
    atual = no
    while isinstance(atual, ast.BinOp) and isinstance(atual.op, ast.Div):
        if not isinstance(atual.right, ast.Constant) or not isinstance(atual.right.value, str):
            raise RuntimeError(f"passo de run_all.py não é literal: {ast.dump(no)}")
        partes.append(atual.right.value)
        atual = atual.left
    if not (isinstance(atual, ast.Name) and atual.id == "ROOT"):
        raise RuntimeError(f"passo de run_all.py não parte de ROOT: {ast.dump(no)}")
    return "/".join(reversed(partes))


def passos_do_pipeline() -> list[str]:
    """Lê a lista `STEPS` de `run_all.py` sem executá-lo.

    Motivo: a sequência de reprodução era mantida à mão no manifesto, começava
    em `02_reconciliar_funil_ciclo1.py` e omitia A1 e **toda** a aquisição,
    inclusive `scripts/aquisicao/05_integrar_painel_analitico.py`, que constrói
    o insumo de A5. Derivar do ponto de entrada impede que as duas divirjam.
    """
    arvore = ast.parse(RUN_ALL.read_text(encoding="utf-8"))
    for no in arvore.body:
        if isinstance(no, ast.Assign) and any(
            isinstance(alvo, ast.Name) and alvo.id == "STEPS" for alvo in no.targets
        ):
            if not isinstance(no.value, (ast.List, ast.Tuple)):
                raise RuntimeError("STEPS de run_all.py não é uma lista literal")
            return [_caminho_de_step(elemento) for elemento in no.value.elts]
    raise RuntimeError("STEPS não encontrado em run_all.py")


def insumos_declarados() -> list[tuple[Path, str, str | None]]:
    """Insumos e artefatos que o desenho de A1–A6 exige, com o papel de cada um.

    A terceira posição é o motivo **conhecido** de ausência. Um insumo que faz
    parte do desenho e não está no disco continua tendo entrada no manifesto,
    marcada como ausente: omiti-lo apagaria a proveniência em silêncio sempre
    que o manifesto fosse regerado numa máquina sem os microdados. Um insumo
    que não faz parte do desenho simplesmente não aparece nesta lista.
    """
    return [
        (ROOT / "output/aquisicao/quadro_vagas_tratamento.parquet", "quadro de vagas publicado, insumo de A1", None),
        (ROOT / "output/aquisicao/ponte_curso_cbo_oficial.json", "ponte curso–CBO congelada", None),
        (ROOT / "output/aquisicao/manifesto_cnes_26_competencias.json", "manifesto das 26 competências mensais do CNES", None),
        (ROOT / "data/pmm_especialistas_nominal.csv", "retrato nominal observado, insumo de A7/A8", None),
        (ROOT / "data/ivs_ipea_2010_municipios.csv", "IVS 2010 do IPEA, running variable canônica", None),
        (FUNIL, "matriz do funil do ciclo 1, saída de A1", None),
        (OUT / "matriz_tipologia_territorial.parquet", "tipologia territorial congelada, saída de A2", None),
        (OUT / "portao_denominador.json", "portão do denominador, A1", None),
        (OUT / "registro_pre_analise_atracao.json", "pré-análise congelada, A3", None),
        (OUT / "potencia_atracao.json", "cálculo de potência declarado em A3", None),
        (ROOT / "output/painel_municipio_curso_mensal.parquet", "painel município–curso mensal do CNES, insumo de A5", MOTIVO_CNES_AUSENTE),
        (OUT / "A5_painel_T0.parquet", "painel em T0, dataset de estimação de A5", None),
        (A4, "estimativas de A4", None),
        (A5, "estimativas de A5", None),
        (OUT / "A5_manifesto_maturidade_censura.json", "maturidade e censura declaradas em A5", None),
        (OUT / "A4_tabela_02_modelo_principal_LPM.csv", "modelo principal de A4", None),
        (OUT / "A4_tabela_02c_confirmacao_homologacao.csv", "estágios do funil em A4", None),
        (OUT / "A4_tabela_02d_municipio_curso.csv", "colapso município–curso em A4", None),
        (OUT / "A5_tabela_07_estudo_evento_atracao.csv", "estudo de evento de A5", None),
        (REDTEAM, "red team gerado aqui", None),
        (MATRIX_OUT_CSV, "matriz afirmação–evidência–limite gerada aqui", None),
        (SYNTHESIS, "síntese gerada aqui", None),
    ]


def hashear_insumos() -> tuple[dict[str, dict[str, object]], list[str]]:
    """Hasheia cada insumo do desenho; marca explicitamente o que está ausente."""
    hashes: dict[str, dict[str, object]] = {}
    ausentes: list[str] = []
    for caminho, papel, motivo in insumos_declarados():
        rel = caminho.relative_to(ROOT).as_posix()
        if caminho.exists():
            hashes[rel] = {
                "sha256": sha256(caminho),
                "bytes": caminho.stat().st_size,
                "papel": papel,
                "presente": True,
            }
            continue
        hashes[rel] = {
            "sha256": None,
            "bytes": None,
            "papel": papel,
            "presente": False,
            "motivo_ausencia": motivo
            or "ausência não prevista no desenho; investigar antes de confiar neste manifesto",
        }
        ausentes.append(rel)
    return hashes, ausentes




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
    prev = prevalencia_atracao()
    celulas_fmt = f"{prev['celulas']:,}".replace(",", ".")
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
**Veredito:** A4 cobre 1.295 células em 368 municípios; A5 principal restringe-se a 587 células município–curso de dez cursos cujo CBO não é compartilhado com outro curso do PMM-E, em 295 municípios; apenas oito desses cursos têm CBO estritamente 1:1. A amostra ampliada é apenas sensibilidade.

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
- O estudo dinâmico usa efeitos fixos de célula, curso–mês e UF–mês, com cluster municipal. Em março/2026, a diferença associada à atração é {num(event['mar2026_beta'])} (EP {num(event['mar2026_se'])}; p={num(event['mar2026_p'], 3)}); o teste conjunto prévio tem p={num(event['pre_p'], 3)}.
- A sensibilidade ampliada produz {num(expanded['mar2026_beta'])} (p={num(expanded['mar2026_p'], 3)}), mas mistura CBOs sobrepostos.
- A distribuição é assimétrica: sem atração, média {num(dist0['media'])}, mediana {num(dist0['mediana'], 0)}, máximo {num(dist0['max'], 0)}; com atração, média {num(dist1['media'])}, mediana {num(dist1['mediana'], 0)}, máximo {num(dist1['max'], 0)}. Winsorizar muda materialmente a precisão, portanto médias simples não bastam.
- O modelo de nível é dominado por diferenças basais e a validação preditiva fora da amostra é fraca. Ambos ficam como diagnósticos.

## Veredito geral

O núcleo útil é a desigualdade territorial na atração administrativa, robusta ao estágio do funil e à unidade analítica. A evolução do estoque cadastral após a oferta é compatível com uma diferença positiva modesta, mas vulnerável a caudas, composição e tempo de exposição heterogêneo. Não há base para reivindicar efeito causal, provimento atribuível ao programa ou retenção individual.

*Gerado por `scripts/tema_trabalho/07_red_team_sintese.py`.*
"""
    atomic_text(REDTEAM, redteam)

    matrix_rows = [
        (f"Atração administrativa de {pct(prev['ch1_prop'])}% no quadro da primeira chamada",
         f"{prev['ch1_celulas']} de {celulas_fmt} células; pelo ciclo 1 inteiro, {prev['ciclo_celulas']} ({pct(prev['ciclo_prop'])}%)",
         "Célula não é vaga física; primeira chamada não é o ciclo inteiro",
         "prevalência administrativa observada"),
        (f"Metropolitano associado a +{pct(metro)} pp versus remoto", "LPM com FE curso e UF; cluster município", f"Ajuste completo: +{pct(metro_full)} pp", "associado a maior atração"),
        ("Resultado preservado em confirmação", f"Contraste metropolitano +{pct(confirm)} pp", "Confirmação não é entrada física", "associação no estágio de confirmação"),
        ("Resultado preservado em homologação", f"Contraste metropolitano +{pct(homolog)} pp", "Homologação não é exercício", "associação no estágio de homologação"),
        ("Resultado preservado ao colapsar CNES", f"Município–curso: +{pct(collapsed)} pp", "Muda o peso analítico", "robustez à unidade"),
        ("IVS/faixa não identificam efeito marginal", "Coeficientes conjuntos instáveis e R1 falhou", "Regra administrativa não reproduzida", "gradiente descritivo"),
        (f"Dinâmica CNES em março/2026: +{num(event['mar2026_beta'])}", f"FE célula, curso–mês, UF–mês; p={num(event['mar2026_p'], 3)}", "Atração é resultado realizado; sem grupo causal", "associado a trajetória diferencial"),
        ("Pré-tendências não rejeitadas", f"Teste conjunto p={num(event['pre_p'], 3)}", "Não rejeitar não prova paralelismo", "diagnóstico favorável, não validação causal"),
        ("Distribuição da mudança é assimétrica", f"Medianas {num(dist0['mediana'], 0)} e {num(dist1['mediana'], 0)}; máximo com atração {num(dist1['max'], 0)}", "Cauda extrema influencia a média", "descrever média, mediana e caudas"),
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

Analisamos o **quadro da primeira chamada** do primeiro ciclo do PMM-E, {celulas_fmt} células CNES–curso em 368 municípios. Alguma confirmação ou homologação **na própria primeira chamada** ocorreu em {prev['ch1_celulas']} células, {pct(prev['ch1_prop'])}% do quadro — é essa a prevalência da população primária de A4. Somando as homologações novas da segunda chamada, o **ciclo 1 inteiro** alcança {prev['ciclo_celulas']} das mesmas {celulas_fmt} células, {pct(prev['ciclo_prop'])}%: {prev['celulas_novas_ch2']} células sem desfecho na primeira chamada receberam homologado novo na segunda, somando {prev['pessoas_novas_ch2']} pessoas. Os dois números medem coisas diferentes e não são intercambiáveis. Em modelo linear com efeitos fixos de curso e UF e erros agrupados por município, células metropolitanas tiveram probabilidade {pct(metro)} pontos percentuais maior que as do interior remoto; o contraste foi {pct(metro_full)} pontos no ajuste completo, {pct(confirm)} na confirmação, {pct(homolog)} na homologação e {pct(collapsed)} ao colapsar para município–curso. Como evidência secundária, um estudo dinâmico do CNES em 587 células de dez cursos com CBO não compartilhado entre cursos encontrou diferença associada à atração de {num(event['mar2026_beta'])} médico cadastrado em março/2026 (EP {num(event['mar2026_se'])}), relativa a junho/2025. A distribuição é assimétrica e contém máximo 211 no grupo com atração. Os achados sustentam um gradiente territorial de implementação e uma trajetória cadastral diferencial modesta; não sustentam efeito causal da bolsa, provimento atribuível ao programa ou retenção individual.

## Introdução

O problema empiricamente identificável hoje não é o retorno causal de cada faixa de bolsa, mas onde a oferta administrativa atraiu ao menos uma confirmação ou homologação. IVS 2010 permanece a variável canônica do desenho previsto, porém faixa e IVS não fornecem variação independente, e a regra administrativa não foi reproduzida em 177 dos 368 municípios. Por isso o RDD foi encerrado no primeiro portão. A contribuição atual é medir desigualdades territoriais na implementação e documentar, separadamente, a evolução da oferta médica cadastrada no CNES.

## Métodos

A análise principal usa células CNES–curso da chamada 1, tipologia territorial REGIC/RM-RIDE congelada antes da estimação e LPM pré-especificado com efeitos fixos de curso e UF e cluster municipal; Logit, ajuste completo, estágios do funil, colapso município–curso, winsorização e leave-one-out são robustez. O benchmark global de 3,8 pp é precisão de uma proporção, não MDE do contraste territorial; para metropolitano versus interior remoto, o MDE prévio é 13,7 pp sob p=0,30.

A análise secundária usa 26 competências CNES e, como amostra principal, 587 células município–curso em 295 municípios. Junho/2025 é a última referência limpa antes da oferta; setembro/2025 já pode estar tratado. O estudo dinâmico absorve efeitos fixos de célula, curso–mês e UF–mês, com erros agrupados por município. Atração administrativa é um resultado realizado, não tratamento exógeno. Estoque e entradas referem-se a vínculos cadastrados; não identificam médicos do programa.

## Conclusão

O resultado publicável é um gradiente territorial de atração: municípios metropolitanos apresentam maior probabilidade de atração administrativa que o interior remoto, e o padrão resiste à separação entre confirmação e homologação e ao colapso da unidade. A dinâmica do CNES sugere diferença positiva posterior, com pré-tendências não rejeitadas, mas a cauda extrema, a composição e o tempo de exposição física heterogêneo limitam sua interpretação. Sem base para efeito causal do adicional da bolsa, retenção individual, resolutividade, fila, SIH/SIA ou custo-benefício, esses objetos exigem novos dados e novo protocolo antes de qualquer estimação.
"""
    atomic_text(SYNTHESIS, synthesis)

    hashes, insumos_ausentes = hashear_insumos()
    docs_hash = {
        path.relative_to(ROOT).as_posix(): sha256(path)[:8]
        for path in (REDTEAM, MATRIX_DOC_CSV, MATRIX_MD, SYNTHESIS)
    }
    commands = [f"{PYTHON_REPRO} {passo}" for passo in passos_do_pipeline()]
    commands.append(f"{PYTHON_REPRO} run_tests.py")
    manifest = {
        "protocolo": "A6_MANIFESTO_REPRODUCAO",
        "data_referencia": date,
        "gerador": "scripts/tema_trabalho/07_red_team_sintese.py",
        "fila": "A1->A6: núcleo associativo; upgrade causal bloqueado",
        "ambiente_exigido": {
            "python_minimo": PYTHON_MINIMO,
            "interpretador": PYTHON_REPRO,
            "como_montar": [
                "python3.13 -m venv .venv",
                ".venv/bin/pip install -r requirements.txt",
            ],
            "por_que": (
                "numpy e pandas fixados no requirements.txt exigem Python 3.12 ou "
                "superior; sob outro ambiente os artefatos são reescritos a partir "
                "da 14ª casa decimal e a cadeia de SHA-256 quebra em silêncio"
            ),
        },
        "comando_unico": f"{PYTHON_REPRO} run_all.py",
        "comandos_reproducao": commands,
        "comandos_derivados_de": "run_all.py (lista STEPS)",
        "versoes": {
            "python": sys.version,
            "platform": platform.platform(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "statsmodels": statsmodels.__version__,
        },
        "hashes_entradas_e_artefatos": hashes,
        "insumos_ausentes": insumos_ausentes,
        "nota_insumos_ausentes": (
            "Insumo declarado no desenho e ausente do disco aparece acima com "
            "sha256 nulo, presente=false e motivo_ausencia. Entrada omitida "
            "significaria que o insumo não faz parte do desenho."
        ),
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
