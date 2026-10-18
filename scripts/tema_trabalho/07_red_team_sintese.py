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

try:
    # Só registra a versão no manifesto: nenhuma estimação deste gerador usa
    # statsmodels, e a ausência dele não pode impedir a regeração dos documentos.
    import statsmodels

    VERSAO_STATSMODELS = statsmodels.__version__
except ModuleNotFoundError:
    VERSAO_STATSMODELS = "ausente no ambiente de geração"


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "tema_trabalho"
AUD = ROOT / "docs" / "auditorias"
EXEC = ROOT / "docs" / "06_execucao"

A4 = OUT / "A4_estimativas_atracao.json"
A5 = OUT / "A5_estimativas_provimento.json"
A5_AMEACAS = OUT / "A5_ameacas_c7.json"
# RDD da bolsa no IVS 2010 oficial (auditoria 16): portão R1, E3 e E5.
RDD = ROOT / "output" / "rdd_bolsa"
R1_OFICIAL = RDD / "portao_r1_ivs_oficial.json"
E3_STATUS = RDD / "E3_status.json"
E3_ESTIMATIVAS = RDD / "E3_estimativas.csv"
E5_ESPECIFICACOES = RDD / "E5_especificacoes.csv"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
IVS_LOCAL = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
DESFECHO_PREENCHIMENTO = "fracao_celulas_ch1_com_confirmacao_ou_homologacao"
# Fator do efeito mínimo detectável a 80% de poder e 5% bilateral (1,96 + 0,84),
# o mesmo de docs/06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md.
FATOR_MDE = 2.8
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


def estado_rdd_bolsa() -> dict[str, object]:
    """Lê dos artefatos o estado vigente da RDD da bolsa e confere o que o texto afirma.

    Este gerador publicava que a regra da faixa não se reproduzia (177/368) e
    que a RDD fora encerrada em R1. Isso vinha de
    `data/ivs_ipea_2010_municipios.csv`, que é, em cada município, a linha de um
    subgrupo populacional da base do Ipea e não o IVS do município (auditoria
    16). Com o IVS 2010 oficial, R1 é APROVADO_SHARP e o E3 não encontra salto
    distinguível de zero. Os números saem dos artefatos; se eles deixarem de
    sustentar "aprovado sharp" ou "inconclusivo", o gerador para em vez de
    publicar texto falso.
    """
    r1 = json.loads(R1_OFICIAL.read_text(encoding="utf-8"))
    if r1["decisao_r1"] != "APROVADO_SHARP":
        raise SystemExit(f"R1: o texto afirma APROVADO_SHARP; o artefato traz {r1['decisao_r1']}")
    populacoes = r1["populacoes"]
    for pop in ("P1", "P2"):
        if populacoes[pop]["regra_reproduz"] != populacoes[pop]["municipios"]:
            raise SystemExit(f"R1: o texto afirma a regra reproduzida em todo {pop}; o artefato diverge")
    escore_iguais = str(r1["escore_administrativo_e_ivs_2010_oficial"]["valores_iguais_3_casas"])
    iguais, total = (int(x) for x in escore_iguais.split("/"))
    if iguais != total:
        raise SystemExit(f"R1: o texto afirma escore do MS igual ao IVS oficial; o artefato traz {escore_iguais}")

    status = json.loads(E3_STATUS.read_text(encoding="utf-8"))
    if status["status"] != "CONCLUIDO":
        raise SystemExit(f"E3: o texto cita estimativas concluídas; o status é {status['status']}")
    cortes = [float(c) for c in status["cortes"]]
    h = float(status["janelas"]["principal"])

    e3 = pd.read_csv(E3_ESTIMATIVAS)
    principal = e3[e3["especificacao"].eq("principal") & e3["h"].round(3).eq(round(h, 3))]
    if len(principal) != 3 * len(cortes):
        raise SystemExit(f"E3: esperava {3 * len(cortes)} saltos principais; o artefato traz {len(principal)}")
    if (e3["p_valor"] < 0.05).any():
        raise SystemExit("E3: o texto afirma nenhum salto distinguível de zero; há p < 0,05 no artefato")
    saltos_brl = set(e3["salto_anunciado_brl"].astype(int))
    if len(saltos_brl) != 1 or next(iter(saltos_brl)) % 1000:
        raise SystemExit(f"E3: o texto cita um único salto anunciado em mil reais; o artefato traz {sorted(saltos_brl)}")
    preenchimento = {}
    for corte in cortes:
        linha = principal[
            principal["populacao"].eq("P1")
            & principal["outcome"].eq(DESFECHO_PREENCHIMENTO)
            & principal["corte"].round(3).eq(round(corte, 3))
        ]
        if len(linha) != 1:
            raise SystemExit(f"E3: esperava uma linha principal do preenchimento em {corte}; há {len(linha)}")
        preenchimento[corte] = linha.iloc[0]

    # E5 é exploratório e posterior ao resultado; o texto só diz que ele não muda
    # a leitura, e isso tem de continuar verdadeiro no artefato.
    e5 = pd.read_csv(E5_ESPECIFICACOES)
    y1 = e5[e5["outcome"].eq("Y1")]
    if (e5["p_valor"] < 0.05).any() or y1["descarta_tau_ge_010"].astype(bool).any():
        raise SystemExit("E5: o texto afirma que a inferência alternativa não muda a leitura; o artefato diverge")

    return {
        "p1": int(populacoes["P1"]["municipios"]),
        "p2": int(populacoes["P2"]["municipios"]),
        "escore_iguais": iguais,
        "cortes": cortes,
        "h": h,
        "salto_mil": next(iter(saltos_brl)) // 1000,
        "preenchimento": preenchimento,
        "n_saltos": int(len(e3)),
        "janelas": sorted(float(j) for j in e3["h"].unique()),
        "p_min": float(e3["p_valor"].min()),
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
        (IVS_LOCAL, "arquivo local rebaixado (auditoria 16): linha de subgrupo populacional da base do Ipea, "
         "não o IVS do município; não é running variable nem covariável; nenhuma etapa de A2 a A5 o lê desde "
         "18/10/2026 (auditoria 19); hasheado só como registro do failure mode", None),
        (IVS_OFICIAL, "IVS 2010 oficial do Ipea (= escore administrativo do MS), running variable canônica da RDD da bolsa", None),
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
        (A5_AMEACAS, "placebo, pré-tendência por curso e deslocamento regional de A5 (C-7)", None),
        (R1_OFICIAL, "portão R1 da RDD da bolsa com o IVS 2010 oficial (APROVADO_SHARP)", None),
        (E3_STATUS, "status, protocolo e cobertura do E3, RDD sharp da bolsa", None),
        (E3_ESTIMATIVAS, "estimativas do E3, RDD sharp da bolsa", None),
        (E5_ESPECIFICACOES, "inferência alternativa da RDD da bolsa (E5, exploratória e pós-resultado)", None),
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
    c7 = json.loads(A5_AMEACAS.read_text(encoding="utf-8"))
    m4 = a4["modelos"]
    m5 = a5["modelos"]

    metro = m4["primario_LPM_minimal"]["coef_estrato"]["estrato_metropolitano"]
    metro_full = m4["sensibilidade_full"]["coef_estrato_full"]["estrato_metropolitano"]
    confirm = m4["robustez_estagios_funil"]["alguma_confirmacao"]["coef_estrato"]["estrato_metropolitano"]
    homolog = m4["robustez_estagios_funil"]["alguma_homologacao"]["coef_estrato"]["estrato_metropolitano"]
    collapsed = m4["robustez_municipio_curso"]["coef_estrato"]["estrato_metropolitano"]
    event = m5["principal_dinamico_confirmatorio"]
    expanded = m5["sensibilidade_dinamica_ampliada"]
    prop = m5["principal_proporcional_confirmatorio"]
    loo_prop = [e for e in a5["leave_one_curso_evento"] if e["escala"] == "proporcional"]
    loo_nivel = [e for e in a5["leave_one_curso_evento"] if e["escala"] == "nivel"]
    prop_um_fora = [e for e in loo_prop if e["subamostra"].startswith("sem_curso_")]
    prop_min = min(prop_um_fora, key=lambda e: e["beta"])
    prop_max = max(prop_um_fora, key=lambda e: e["beta"])
    prop_estritos = next(e for e in loo_prop if e["subamostra"] == "somente_8_cbo_1_para_1")
    nivel_estritos = next(e for e in loo_nivel if e["subamostra"] == "somente_8_cbo_1_para_1")
    nivel_sem14 = next(e for e in loo_nivel if e["subamostra"] == "sem_curso_14")
    dist0 = m5["distribuicao_delta_confirmatoria"]["0"]
    dist1 = m5["distribuicao_delta_confirmatoria"]["1"]
    prev = prevalencia_atracao()
    # C-7: as três ameaças, lidas do artefato gerado sob protocolo congelado.
    q_prop = a5["multiplicidade"]["mar2026_q_fdr_bh_gl_fe_proporcional_confirmatoria"]
    q_nivel = a5["multiplicidade"]["mar2026_q_fdr_bh_gl_fe_nivel_confirmatoria"]
    pl_n = c7["placebo"]["resultado"]["nivel"]
    reaud = c7["placebo"]["comparacao_reauditoria_nivel"]  # lida do protocolo C-7 pelo 06b
    pl_p = c7["placebo"]["resultado"]["proporcional"]
    pre = c7["pretendencia_por_curso"]
    cursos_rej = pre["cursos_pre_p_lt_0_05_proporcional"]
    cursos_rej_nivel = pre["cursos_pre_p_lt_0_05_nivel"]
    posto_baixo = sorted(int(c) for c, esc in pre["por_curso"].items() if not esc["proporcional"]["pre_F_confiavel"])
    sens_p = pre["sensibilidade_excluindo_cursos_rejeitados"]["proporcional"]
    sens_n = pre["sensibilidade_excluindo_cursos_rejeitados"]["nivel"]
    tr_n = c7["deslocamento"]["transbordo"]["nivel"]
    tr_p = c7["deslocamento"]["transbordo"]["proporcional"]
    rg_n = c7["deslocamento"]["oferta_liquida_regional"]["nivel"]
    rg_p = c7["deslocamento"]["oferta_liquida_regional"]["proporcional"]
    dec = c7["deslocamento"]["decomposicao_oferta_liquida"]
    rgm_p = dec["multi_municipio"]["proporcional"]
    rgm_n = dec["multi_municipio"]["nivel"]
    rgu_p = dec["um_unico_municipio"]["proporcional"]
    n_multi = dec["n_regiao_curso_multi_municipio"]
    n_uni = dec["n_regiao_curso_um_municipio"]
    n_mistas = c7["deslocamento"]["n_regiao_curso_com_municipio_atraido_e_nao_atraido"]
    mult_pre = c7["pretendencia_por_curso"]["multiplicidade"]
    cursos_q_prop = mult_pre["cursos_q_lt_0_05_proporcional"]
    q_por_curso_prop = mult_pre["q_por_curso"]["proporcional"]
    p_curso2_prop = pre["por_curso"]["2"]["proporcional"]["pre_p_gl_fe"]
    lista = lambda xs: ", ".join(str(x) for x in xs) if xs else "nenhum"
    celulas_fmt = f"{prev['celulas']:,}".replace(",", ".")
    # Contagens das amostras lidas dos artefatos de A4 e A5 (não digitadas).
    a4_mun = int(m4["primario_LPM_minimal"]["n_clusters"])
    a5_cel, a5_mun, a5_cursos = int(event["n_celulas"]), int(event["n_clusters"]), int(event["n_cursos"])
    # Data de referência dos insumos (A4 e A5 a gravam a partir do protocolo), não do relógio.
    date = max(str(a4.get("data_referencia", "")), str(a5.get("data_referencia", "")))

    # RDD da bolsa: estado vigente lido de R1, E3 e E5 (auditoria 16).
    rdd = estado_rdd_bolsa()
    c1, c2 = (num(c, 3) for c in rdd["cortes"])
    p1, p2 = rdd["p1"], rdd["p2"]
    salto = f"R$ {rdd['salto_mil']} mil"
    y_c1, y_c2 = (rdd["preenchimento"][c] for c in rdd["cortes"])
    tau_c1, tau_c2 = pct(y_c1["tau"]), pct(y_c2["tau"])
    ic_c1 = f"[{pct(y_c1['ic95_inf'])}; {pct(y_c1['ic95_sup'])}]"
    ic_c2 = f"[{pct(y_c2['ic95_inf'])}; {pct(y_c2['ic95_sup'])}]"
    mde_c1, mde_c2 = pct(FATOR_MDE * y_c1["ep"]), pct(FATOR_MDE * y_c2["ep"])
    p_min_e3 = num(rdd["p_min"], 3)
    janelas_txt = [num(j, 3) for j in rdd["janelas"]]
    janelas_e3 = ", ".join(janelas_txt[:-1]) + f" e {janelas_txt[-1]}" if len(janelas_txt) > 1 else janelas_txt[0]
    # Ajuste completo de A4, reestimado em 18/10/2026 com a base oficial (IVS e
    # população 2010 do Ipea; Censo 2022 no denominador do estoque). A versão
    # anterior usava o arquivo local errado; seus números ficam só na auditoria 19.
    aj = pd.read_csv(OUT / "A4_tabela_03b_ajuste_completo.csv").set_index("termo").loc["estrato_metropolitano"]
    p_full, q_full = float(aj["p_valor"]), float(aj["q_fdr_estrato"])
    ressalva_full = (
        f"usa IVS e população 2010 da base oficial do Ipea e o estoque por 10 mil habitantes do Censo 2022 "
        f"(p={num(p_full, 3)}; q de FDR nos três estratos={num(q_full, 3)}); a versão com o arquivo local "
        "errado (auditoria 16) só consta como failure mode (auditoria 19)"
    )
    pot = json.loads((OUT / "potencia_atracao.json").read_text(encoding="utf-8"))
    bench_global = pct(pot["mde_global"]["mde_80_pp_p30"])
    mde_metro = pct(pot["contrastes_vs_interior_remoto"]["metropolitano"]["mde_80_pp_p30"])

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
**Veredito:** A4 cobre {celulas_fmt} células em {a4_mun} municípios; A5 principal restringe-se a {a5_cel} células município–curso de {a5_cursos} cursos cujo CBO não é compartilhado com outro curso do PMM-E, em {a5_mun} municípios; apenas oito desses cursos têm CBO estritamente 1:1. A amostra ampliada é apenas sensibilidade.

### 4. Inferência municipal e concentração

**Refutação tentada:** usar erros independentes por célula e ignorar exposição comum dentro do município.  
**Veredito:** erros agrupados por município em todos os modelos principais. Leave-one-out (LOO) por UF, curso e município e diagnóstico de influência permanecem obrigatórios.

### 5. Confirmação, homologação, entrada e permanência

**Refutação tentada:** chamar confirmação de entrada física ou presença cadastral de retenção.  
**Veredito:** os estágios são separados. Em A4, o contraste metropolitano é {pct(confirm)} pp para confirmação e {pct(homolog)} pp para homologação. Em A5, “entrada” é um novo vínculo no mês após washout de seis meses, não um fluxo acumulado semestral.

### 6. IVS e faixa de bolsa

**Refutação tentada:** interpretar IVS, faixa e valor anunciado como fontes independentes de variação.  
**Veredito:** não são independentes. A faixa é função determinística do IVS 2010 oficial do Ipea, com cortes em {c1} e {c2} (regra reproduzida em {p1}/{p1} municípios do ciclo 1 e {p2}/{p2} do ciclo 2), e o valor anunciado é função da faixa. Fora dos cortes, IVS e faixa descrevem o território e só sustentam gradiente descritivo; nos cortes, a descontinuidade isola o incentivo marginal anunciado (item 8). O IVS 2010 oficial (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`) é a running variable canônica. A divergência de regra registrada antes vinha de `data/ivs_ipea_2010_municipios.csv`, que é, em cada município, a linha de um subgrupo populacional da base do Ipea e não o IVS do município (`docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md`); o arquivo foi rebaixado.

### 7. CNES e retenção individual

**Refutação tentada:** usar estoque municipal do CBO para afirmar permanência do bolsista.  
**Veredito:** CNES mede oferta cadastrada agregada. Sem ponte nominal validada, não identifica participação no PMM-E nem retenção individual.

### 8. RDD

**Refutação tentada:** ler a RDD do adicional de bolsa como efeito do PMM-E, ler a ausência de salto como prova de que a bolsa não funciona, ou trocar a especificação depois de ver o resultado.  
**Veredito:** com o IVS 2010 oficial, R1 é APROVADO_SHARP: a regra se reproduz em {p1}/{p1} municípios do ciclo 1 e {p2}/{p2} do ciclo 2, e o escore do MS coincide com o IVS oficial nos {rdd['escore_iguais']} municípios em que é publicado. O E3 (local linear, kernel triangular, h = {num(rdd['h'], 3)}, EP HC1 por município, protocolo congelado e retrospectivo) não encontra salto distinguível de zero: na fração de células preenchidas na primeira chamada do ciclo 1, {tau_c1} pp {ic_c1} em {c1} e {tau_c2} pp {ic_c2} em {c2}; nenhum dos {rdd['n_saltos']} saltos estimados, com as janelas de {janelas_e3}, tem p < 0,05 (menor p = {p_min_e3}). Com efeito mínimo detectável ({num(FATOR_MDE, 1)} × EP) de {mde_c1} e {mde_c2} pp na fração preenchida, o resultado é inconclusivo, e não evidência de ineficácia. O contraste identificável é só o incentivo marginal anunciado de {salto}, local aos cortes e possivelmente somado a outros benefícios ligados às mesmas categorias de IVS; não é efeito do PMM-E, do programa nem da faixa como nível. A inferência alternativa (E5, `docs/06_execucao/39_inferencia_alternativa_rdd_bolsa.md`), exploratória e posterior ao resultado, não muda essa leitura.

### 9. SIH/SIA, fila, saúde e custo-benefício

**Refutação tentada:** extrapolar estoque cadastral para resolutividade, internações, fila ou retorno econômico.  
**Veredito:** sem SIH/SIA e sem portão de linkage/pagamentos, esses desfechos ficam fora do núcleo empírico atual.

## Ataques ao resultado principal (A4)

- O contraste metropolitano versus interior remoto é {pct(metro)} pp no LPM pré-especificado e {pct(metro_full)} pp no ajuste completo, que {ressalva_full}. Os coeficientes de estrato do LPM pré-especificado nunca dependeram do arquivo local.
- Separar o funil preserva o sinal: {pct(confirm)} pp em confirmação e {pct(homolog)} pp em homologação.
- Colapsar múltiplos CNES para município–curso aumenta o contraste para {pct(collapsed)} pp; logo, o resultado não decorre do peso implícito de estabelecimentos múltiplos.
- Winsorizar covariadas e executar leave-one-out não inverte o gradiente. O resultado é robusto como associação territorial, não como efeito da bolsa.

## Ataques ao resultado secundário (A5)

- Setembro/2025 foi rejeitado como baseline porque já contém exposição física. A referência limpa é junho/2025 e o follow-up comum é março/2026.
- O estudo dinâmico usa efeitos fixos de célula, curso–mês e UF–mês, com cluster municipal. Em março/2026, a diferença associada à atração é {num(event['mar2026_beta'])} (EP {num(event['mar2026_se'])}; p={num(event['mar2026_p'], 3)}); o teste conjunto prévio tem p={num(event['pre_p'], 3)}.
- A sensibilidade ampliada produz {num(expanded['mar2026_beta'])} (p={num(expanded['mar2026_p'], 3)}), mas mistura CBOs sobrepostos.
- A distribuição é assimétrica: sem atração, média {num(dist0['media'])}, mediana {num(dist0['mediana'], 0)}, máximo {num(dist0['max'], 0)}; com atração, média {num(dist1['media'])}, mediana {num(dist1['mediana'], 0)}, máximo {num(dist1['max'], 0)}. Winsorizar muda materialmente a precisão, portanto médias simples não bastam.
- O modelo de nível é dominado por diferenças basais e a validação preditiva fora da amostra é fraca. Ambos ficam como diagnósticos.

### Forma funcional: o que é frágil é o nível, não a proporção

**Refutação tentada:** atribuir o resultado secundário à escala de medida, testando se ele sobrevive à troca de nível por proporção e à retirada de cada curso.
**Veredito:** a fragilidade é **do nível**, e é específica dele. Em nível, o coeficiente de março/2026 cai de {num(event['mar2026_beta'])} para {num(nivel_sem14['beta'])} sem o curso 14 (p={num(nivel_sem14['p_valor'], 3)}) e para {num(nivel_estritos['beta'])} nos oito cursos com CBO estritamente 1:1 (p={num(nivel_estritos['p_valor'], 3)}) — deixa de ser distinguível de zero. Somar profissionais de municípios com estoques de ordens de grandeza diferentes faz um curso de estoque grande dominar o coeficiente mecanicamente.

Na escala proporcional, que é a primária, o mesmo exercício não desfaz o resultado: {num(prop['mar2026_beta'], 3)} (EP {num(prop['mar2026_se'], 3)}; p={num(prop['mar2026_p'], 4)}) na amostra completa, entre {num(prop_min['beta'], 3)} e {num(prop_max['beta'], 3)} ao retirar um curso por vez, e {num(prop_estritos['beta'], 3)} (p={num(prop_estritos['p_valor'], 3)}) nos oito cursos estritos. O enunciado correto, portanto, não é o de vulnerabilidade genérica a caudas que este documento trazia antes do item C2 do plano `35`: é que **o nível é frágil à composição de cursos e a proporção não é**. A escolha da escala proporcional é substantiva — mede variação relativa da oferta local, que é a pergunta pretendida — e vale nas duas direções do resultado. A multiplicidade aponta na mesma direção (item B-5): na família dos 25 coeficientes de evento da amostra confirmatória, o coeficiente de março/2026 tem q de Benjamini–Hochberg de {num(q_prop, 4)} na escala proporcional e de {num(q_nivel, 3)} em nível — só a proporção sobrevive.

### Placebo, pré-tendência por curso e deslocamento (C-7)

As três ameaças que a reauditoria independente levantou foram testadas em 16/09/2026 sob protocolo congelado antes da execução (`docs/06_execucao/36_backlog_pos_auditoria.md`, item C-7), a partir do painel congelado de A5 com hash conferido contra este manifesto. Resultados em `A5_ameacas_c7.json` e nas tabelas `A5_tabela_12` a `A5_tabela_14`; inferência na convenção que conta os efeitos fixos absorvidos.

**Placebo — células sem atração em municípios com atração.** Refutação tentada: o resultado principal seria choque municipal correlacionado com atrair, e não a atração da própria célula. Entre as células confirmatórias sem atração ({pl_n['n_tratadas']} em municípios com atração em alguma célula, {pl_n['n_controle']} em municípios sem nenhuma), o coeficiente de março/2026 é {num(pl_n['mar2026_beta'], 3)} em nível (EP {num(pl_n['mar2026_se_gl_fe'], 3)}; p={num(pl_n['mar2026_p_gl_fe'], 3)}; pré-F {num(pl_n['pre_F_gl_fe'])}, p={num(pl_n['pre_p_gl_fe'], 3)}) e {num(pl_p['mar2026_beta'], 4)} na escala proporcional (p={num(pl_p['mar2026_p_gl_fe'], 3)}). **Veredito:** o placebo passa nas duas escalas; a reauditoria havia medido {num(reaud['beta'], 3)} (EP {num(reaud['se'], 3)}; p={num(reaud['p'], 3)}) em nível, mesma ordem e mesma leitura. O resultado principal é da célula, não do município.

**Heterogeneidade de pré-tendência por curso.** Refutação tentada: o p agregado do teste pré esconderia cursos com caminhos pré divergentes. Dentro de cada um dos dez cursos, o teste conjunto dos doze coeficientes pré rejeita a 5% na escala proporcional nos cursos {lista(cursos_rej)} e, em nível, nos cursos {lista(cursos_rej_nivel)} — os mesmos que a reauditoria apontara (2, 14 e 16 em nível). Nos cursos {lista(posto_baixo)} a covariância das restrições não tem posto completo (poucos municípios), e o F conjunto não é confiável; o curso 16 está entre eles. Pela regra fixada no protocolo, excluindo os cursos rejeitados na escala proporcional o coeficiente de março/2026 vai a {num(sens_p['mar2026_beta'], 4)} (EP {num(sens_p['mar2026_se_gl_fe'], 4)}; p={num(sens_p['mar2026_p_gl_fe'], 4)}) na proporção e a {num(sens_n['mar2026_beta'], 3)} (p={num(sens_n['mar2026_p_gl_fe'], 3)}) em nível, sobre {sens_p['n_unidades']} células. Sob a correção de multiplicidade que o item B-5 adotou para as demais famílias de A5, aplicada aqui à família dos dez testes por curso (item C-7b, posterior ao protocolo), só o curso {lista(cursos_q_prop)} mantém q abaixo de 5% na escala proporcional: o curso 2 passa de p={num(p_curso2_prop, 4)} a q={num(q_por_curso_prop["2"], 3)}, e o curso 16 fica em q={num(q_por_curso_prop["16"], 4)} — justamente o curso cujo F conjunto não é confiável por posto incompleto. Duas rejeições a 5% em dez testes ocorrem com probabilidade próxima de 9% sob o nulo global. **Veredito:** a heterogeneidade por curso fica publicada, mas com ressalva: na escala que governa a regra de exclusão, nenhum dos dois cursos passa ao mesmo tempo pela correção de multiplicidade e pelo posto da covariância. A regra de exclusão continua a pré-registrada, sobre o p cru, e a escala proporcional não é desfeita por ela.

**Deslocamento dentro da região de saúde.** Refutação tentada: o ganho do município com atração sairia de vizinhos da mesma região, sem expansão líquida — a separação que o `CLAUDE.md` exige. (a) Entre células sem atração, as expostas a outro município do painel na mesma região com atração no mesmo curso ({tr_n['n_tratadas']} contra {tr_n['n_controle']}) não perdem estoque: {num(tr_n['mar2026_beta'], 3)} em nível (p={num(tr_n['mar2026_p_gl_fe'], 3)}) e {num(tr_p['mar2026_beta'], 4)} na proporção (p={num(tr_p['mar2026_p_gl_fe'], 3)}). (b) Somando o estoque por região–curso sobre os municípios do painel ({rg_n['n_clusters']} regiões; {rg_n['n_tratadas']} região–curso com atração contra {rg_n['n_controle']} sem), a diferença de março/2026 é {num(rg_n['mar2026_beta'], 3)} em nível (EP {num(rg_n['mar2026_se_gl_fe'], 3)}; p={num(rg_n['mar2026_p_gl_fe'], 3)}) e {num(rg_p['mar2026_beta'], 4)} na proporção (p={num(rg_p['mar2026_p_gl_fe'], 3)}), com pré-F de {num(rg_p['pre_F_gl_fe'])} (p={num(rg_p['pre_p_gl_fe'], 3)}). Decompondo (b) (item C-7c, posterior ao protocolo): das {n_multi + n_uni} região–curso, só {n_multi} agregam mais de um município do painel, e só {n_mistas} contêm ao mesmo tempo município que atraiu e município que não atraiu — a única configuração em que realocação dentro da região é observável. Restrito às {n_multi} que de fato agregam, o coeficiente de março/2026 é {num(rgm_p['mar2026_beta'], 4)} na proporção (EP {num(rgm_p['mar2026_se_gl_fe'], 4)}; p={num(rgm_p['mar2026_p_gl_fe'], 3)}) e {num(rgm_n['mar2026_beta'], 3)} em nível (p={num(rgm_n['mar2026_p_gl_fe'], 3)}); restrito às {n_uni} de um único município, em que o agregado regional é a própria célula, é {num(rgu_p['mar2026_beta'], 4)} (p={num(rgu_p['mar2026_p_gl_fe'], 3)}). **Veredito:** não há sinal de deslocamento a partir dos vizinhos observados em (a); em (b), a significância vem da parte em que não há agregação nenhuma, e na parte informativa o coeficiente não é distinguível de zero. O teste (b) não sustenta afirmar que a oferta regional agregada sobe, nem exclui realocação dentro da região: ele é, em sua maior parte, o resultado da célula com outro rótulo e outro agrupamento. **Limite declarado:** o painel só contém os 368 municípios do quadro, de modo que "vizinho" é vizinho dentro do quadro; deslocamento a partir de municípios fora da oferta não é observável aqui, e a leitura continua associativa.

## Veredito geral

O núcleo útil é a desigualdade territorial na atração administrativa, robusta ao estágio do funil e à unidade analítica. A evolução do estoque cadastral após a oferta é compatível com uma diferença positiva modesta: na escala proporcional ela sobrevive à retirada de qualquer curso e à restrição aos CBOs estritos; na escala de nível, não. O que limita a leitura é a composição de cursos no nível, a pré-tendência divergente em dois cursos, o tempo de exposição física heterogêneo e o fato de que o teste de deslocamento só vê vizinhos dentro do quadro. O placebo passa. O teste de oferta líquida regional, porém, não acrescenta o que se lhe atribuía: {n_uni} das {n_multi + n_uni} região–curso contêm um único município, e restrito às {n_multi} que de fato agregam o coeficiente não é distinguível de zero — deslocamento dentro da região permanece não testado, e não refutado. Não há base para reivindicar efeito causal, provimento atribuível ao programa ou retenção individual.

*Gerado por `scripts/tema_trabalho/07_red_team_sintese.py`.*
"""
    atomic_text(REDTEAM, redteam)

    matrix_rows = [
        (f"Atração administrativa de {pct(prev['ch1_prop'])}% no quadro da primeira chamada",
         f"{prev['ch1_celulas']} de {celulas_fmt} células; pelo ciclo 1 inteiro, {prev['ciclo_celulas']} ({pct(prev['ciclo_prop'])}%)",
         "Célula não é vaga física; primeira chamada não é o ciclo inteiro",
         "prevalência administrativa observada"),
        (f"Metropolitano associado a +{pct(metro)} pp versus remoto", "LPM com FE curso e UF; cluster município",
         f"Ajuste completo: +{pct(metro_full)} pp; {ressalva_full}", "associado a maior atração"),
        ("Resultado preservado em confirmação", f"Contraste metropolitano +{pct(confirm)} pp", "Confirmação não é entrada física", "associação no estágio de confirmação"),
        ("Resultado preservado em homologação", f"Contraste metropolitano +{pct(homolog)} pp", "Homologação não é exercício", "associação no estágio de homologação"),
        ("Resultado preservado ao colapsar CNES", f"Município–curso: +{pct(collapsed)} pp", "Muda o peso analítico", "robustez à unidade"),
        ("IVS/faixa, como níveis, não identificam efeito marginal",
         f"Faixa é função determinística do IVS 2010 oficial: regra reproduzida em {p1}/{p1} (ciclo 1) e {p2}/{p2} (ciclo 2); R1 aprovado sharp",
         "Fora dos cortes, colineares com o território; coeficientes de IVS do A4 reestimados com a base oficial do Ipea em 18/10/2026; a versão com o arquivo local errado só consta como failure mode (auditorias 16 e 19)",
         "gradiente descritivo"),
        (f"Dinâmica CNES em março/2026: +{num(event['mar2026_beta'])}", f"FE célula, curso–mês, UF–mês; p={num(event['mar2026_p'], 3)}", "Atração é resultado realizado; sem grupo causal", "associado a trajetória diferencial"),
        ("Pré-tendências não rejeitadas", f"Teste conjunto p={num(event['pre_p'], 3)}", "Não rejeitar não prova paralelismo", "diagnóstico favorável, não validação causal"),
        ("Distribuição da mudança é assimétrica", f"Medianas {num(dist0['mediana'], 0)} e {num(dist1['mediana'], 0)}; máximo com atração {num(dist1['max'], 0)}", "Cauda extrema influencia a média", "descrever média, mediana e caudas"),
        ("CNES não mede retenção individual", "Agregação município–curso", "Sem ponte nominal de bolsistas", "oferta médica cadastrada local"),
        ("RDD da bolsa sem salto detectável; SIH/SIA e custo-benefício fora do núcleo",
         f"E3 na fração preenchida: {tau_c1} pp {ic_c1} em {c1} e {tau_c2} pp {ic_c2} em {c2}; menor p {p_min_e3}; bases/portões de SIH/SIA ausentes",
         f"RDD: só o incentivo marginal anunciado de {salto}, local aos cortes; MDE de {mde_c1} e {mde_c2} pp. SIH/SIA: sem identificação ou linkage",
         "RDD inconclusiva, não evidência de ineficácia; SIH/SIA: não afirmar sem novo desenho"),
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
> **Nível de identificação:** associativo no núcleo A1–A5. RDD da bolsa em camada separada: R1 aprovado sharp com o IVS 2010 oficial; E3 inconclusivo. Retenção individual não identificada.  
> **Hashes:** A4 `{sha256(A4)[:8]}`; A5 `{sha256(A5)[:8]}`; R1 `{sha256(R1_OFICIAL)[:8]}`; E3 `{sha256(E3_ESTIMATIVAS)[:8]}`.

## Resumo

Analisamos o **quadro da primeira chamada** do primeiro ciclo do PMM-E, {celulas_fmt} células CNES–curso em {a4_mun} municípios. Alguma confirmação ou homologação **na própria primeira chamada** ocorreu em {prev['ch1_celulas']} células, {pct(prev['ch1_prop'])}% do quadro — é essa a prevalência da população primária de A4. Somando as homologações novas da segunda chamada, o **ciclo 1 inteiro** alcança {prev['ciclo_celulas']} das mesmas {celulas_fmt} células, {pct(prev['ciclo_prop'])}%: {prev['celulas_novas_ch2']} células sem desfecho na primeira chamada receberam homologado novo na segunda, somando {prev['pessoas_novas_ch2']} pessoas. Os dois números medem coisas diferentes e não são intercambiáveis. Em modelo linear com efeitos fixos de curso e UF e erros agrupados por município, células metropolitanas tiveram probabilidade {pct(metro)} pontos percentuais maior que as do interior remoto; o contraste foi {pct(metro_full)} pontos no ajuste completo, {pct(confirm)} na confirmação, {pct(homolog)} na homologação e {pct(collapsed)} ao colapsar para município–curso; o ajuste completo {ressalva_full}. Como evidência secundária, um estudo dinâmico do CNES em 587 células de dez cursos com CBO não compartilhado entre cursos encontrou diferença associada à atração de {num(event['mar2026_beta'])} médico cadastrado em março/2026 (EP {num(event['mar2026_se'])}), relativa a junho/2025. A distribuição é assimétrica e contém máximo 211 no grupo com atração. Em camada separada, a RDD do adicional de bolsa nos cortes de {c1} e {c2} do IVS 2010 oficial do Ipea, que reproduz a faixa anunciada em {p1} de {p1} municípios do ciclo 1 (R1 aprovado sharp), não encontra salto distinguível de zero na fração de células preenchidas na primeira chamada: {tau_c1} pontos percentuais em {c1} (IC 95% {ic_c1}) e {tau_c2} em {c2} (IC 95% {ic_c2}). O contraste é só o incentivo marginal anunciado de {salto}, local aos cortes; o resultado é inconclusivo, e não evidência de ineficácia. Os achados sustentam um gradiente territorial de implementação e uma trajetória cadastral diferencial modesta; não sustentam efeito causal da bolsa, provimento atribuível ao programa ou retenção individual.

## Introdução

O núcleo A1–A5 não estima o retorno causal de cada faixa de bolsa: mede onde a oferta administrativa atraiu ao menos uma confirmação ou homologação. Faixa e IVS não fornecem variação independente, porque a faixa é função determinística do IVS 2010 oficial do Ipea, com cortes em {c1} e {c2}; a regra se reproduz em {p1} de {p1} municípios do ciclo 1 e em {p2} de {p2} do ciclo 2, e o portão R1 da RDD foi aprovado como sharp. A conclusão anterior, de que a regra não se reproduzia e a RDD não passava do primeiro portão, vinha de `data/ivs_ipea_2010_municipios.csv`, que é a linha de um subgrupo populacional da base do Ipea e não o IVS do município (auditoria 16). Fora dos cortes, IVS e faixa descrevem o território; nos cortes, a descontinuidade isola apenas o incentivo marginal anunciado de {salto}, e a estimação (E3) é inconclusiva. A contribuição do núcleo é medir desigualdades territoriais na implementação e documentar, separadamente, a evolução da oferta médica cadastrada no CNES.

## Métodos

A análise principal usa células CNES–curso da chamada 1, tipologia territorial REGIC/RM-RIDE congelada antes da estimação e LPM pré-especificado com efeitos fixos de curso e UF e cluster municipal; Logit, ajuste completo, estágios do funil, colapso município–curso, winsorização e leave-one-out são robustez. O ajuste completo e sua variante winsorizada usam IVS e população 2010 da base oficial do Ipea e o estoque por 10 mil habitantes do Censo 2022 (auditoria 19). O benchmark global de {bench_global} pp é precisão de uma proporção, não MDE do contraste territorial; para metropolitano versus interior remoto, o MDE prévio é {mde_metro} pp sob p=0,30.

A análise secundária usa 26 competências CNES e, como amostra principal, {a5_cel} células município–curso em {a5_mun} municípios. Junho/2025 é a última referência limpa antes da oferta; setembro/2025 já pode estar tratado. O estudo dinâmico absorve efeitos fixos de célula, curso–mês e UF–mês, com erros agrupados por município. Atração administrativa é um resultado realizado, não tratamento exógeno. Estoque e entradas referem-se a vínculos cadastrados; não identificam médicos do programa.

## Conclusão

O resultado publicável é um gradiente territorial de atração: municípios metropolitanos apresentam maior probabilidade de atração administrativa que o interior remoto, e o padrão resiste à separação entre confirmação e homologação e ao colapso da unidade. A dinâmica do CNES sugere diferença positiva posterior, com pré-tendências não rejeitadas, e a escala proporcional — a primária — resiste à retirada de qualquer curso e à restrição aos CBOs estritos, enquanto a escala de nível não resiste: é o nível que é frágil à composição de cursos. O placebo sobre células sem atração em municípios com atração é nulo e o teste de deslocamento não encontra perda nos vizinhos observados; já o agregado região–curso não sustenta a leitura de expansão líquida, porque {n_uni} das {n_multi + n_uni} região–curso têm um único município e, restrito às {n_multi} que agregam, o coeficiente não é distinguível de zero. O tempo de exposição física heterogêneo, a pré-tendência divergente em dois cursos — um só deles sobrevivendo à correção de multiplicidade — e o alcance do teste de deslocamento, restrito ao quadro, continuam limitando a interpretação. A RDD do adicional de bolsa, camada separada deste núcleo, não encontra salto distinguível de zero nos cortes de {c1} e {c2} do IVS 2010 oficial: identifica só o incentivo marginal anunciado de {salto}, local aos cortes; o resultado é inconclusivo, e não evidência de ineficácia. Sem base para efeito causal sobre retenção individual, resolutividade, fila, SIH/SIA ou custo-benefício, esses objetos exigem novos dados e novo protocolo antes de qualquer estimação.
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
        "fila": "A1->A6: núcleo associativo; RDD da bolsa em camada separada (R1 aprovado sharp; E3 inconclusivo)",
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
            "statsmodels": VERSAO_STATSMODELS,
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
            "R1_RDD_APROVADO_SHARP": R1_OFICIAL.relative_to(ROOT).as_posix(),
            "E3_RDD_INCONCLUSIVO": E3_STATUS.relative_to(ROOT).as_posix(),
        },
        "limites_reafirmados": [
            "Sem taxa por vaga física",
            (f"Bolsa: o contraste identificável é só o incentivo marginal anunciado de {salto}, local aos cortes "
             f"{c1} e {c2} do IVS 2010 oficial e possivelmente somado a outros benefícios das mesmas categorias; "
             "IVS e faixa como níveis não identificam efeito"),
            "RDD da bolsa inconclusiva: nenhum salto distinguível de zero, o que não é evidência de ineficácia",
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
            "rdd_R1_aprovado_sharp_E3_inconclusivo",
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
