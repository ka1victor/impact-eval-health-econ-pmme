"""A5 — ameaça de política concorrente: o Programa Mais Acesso a Especialistas (PMAE) no CNES-HB.

Pergunta, e só ela: as células com atração do A5 estão mais expostas a uma habilitação
concorrente do mesmo pacote de políticas, na mesma janela do A5, do que as células sem
atração? Se estiverem, parte da evolução diferencial do estoque cadastrado pode ser da
política concorrente. O script NÃO reestima o A5, não muda amostra, desfecho, janela ou
estimador, e não consulta outcome: compara exposição entre grupos.

Fonte: CNES-HB (habilitações por estabelecimento), FTP do DATASUS,
`/dissemin/publicos/CNES/200508_/Dados/HB/HB{UF}{AAMM}.dbc`, um arquivo por UF e
competência. O grupo `3801` é "PROGRAMA MAIS ACESSO A ESPECIALISTAS" segundo
`DBF/HABILITA.DBF` de `Auxiliar/TAB_CNES.zip` no mesmo FTP. Cada arquivo traz as
habilitações vigentes na competência, com `CMPT_INI` (início da vigência) e `DTPORTAR`.

Competências lidas: 202506 (referência do A5) e 202603 (follow-up do A5). Exposição por
município (código IBGE de 6 dígitos, `CODUFMUN`):
- `pmae_vigente_ref`: algum estabelecimento com `3801` vigente em 202506;
- `pmae_novo_janela`: algum `3801` vigente em 202603 com `CMPT_INI` entre 202507 e 202603;
- `pmae_entrada_janela`: `pmae_novo_janela` em município sem `3801` vigente em 202506.

Cuidado medido em outro repositório (`econ_research_theme_validation`, nota
`02-saude/80`): os arquivos mensais do HB anteriores a 2016 foram regravados em lote,
mas os de 2025 e 2026 são gravados cerca de um mês depois da competência, então as duas
vintages usadas aqui são contemporâneas. A mesma nota mediu que habilitação não prediz,
no SIA nem no SIH, entrada de subgrupo de produção novo no estabelecimento: exposição ao
PMAE aqui é exposição a um ato administrativo, não evidência de oferta nova.

Proveniência: o bruto vai para `data/raw/cnes/hb/` (ignorado pelo git), com SHA-256 no
manifesto. A saída não tem CPF nem CNPJ (o campo `CPF_CNPJ` do HB não é lido).
Linguagem: tudo associativo; atração é resultado administrativo realizado.
"""

from __future__ import annotations

import datetime as dt
import ftplib
import hashlib
import io
import json
import shutil
import tempfile
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "cnes" / "hb"
OUT = ROOT / "output" / "tema_trabalho"
PAINEL = OUT / "A5_painel_T0.parquet"
HOST = "ftp.datasus.gov.br"
DIR = "/dissemin/publicos/CNES/200508_/Dados/HB/"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
       "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
REF, FOLLOW = 202506, 202603
GRUPO = "3801"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def baixar(nome: str) -> bytes:
    """Baixa uma vez e reusa o bruto: retomavel por arquivo."""
    destino = RAW / nome
    if destino.exists() and destino.stat().st_size > 0:
        return destino.read_bytes()
    buf = io.BytesIO()
    with ftplib.FTP(HOST, timeout=120) as ftp:
        ftp.login()
        ftp.retrbinary(f"RETR {DIR}{nome}", buf.write)
    RAW.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(buf.getvalue())
    time.sleep(1)  # uma requisicao por segundo no host do DATASUS
    return buf.getvalue()


def ler_dbc(conteudo: bytes) -> pd.DataFrame:
    import pyreaddbc
    from dbfread import DBF

    # pyreaddbc nao abre caminho com acento; a pasta temporaria do sistema evita isso
    tmp = Path(tempfile.mkdtemp(prefix="hb_"))
    try:
        (tmp / "x.dbc").write_bytes(conteudo)
        pyreaddbc.dbc2dbf(str(tmp / "x.dbc"), str(tmp / "x.dbf"))
        campos = ["CNES", "CODUFMUN", "SGRUPHAB", "CMPT_INI", "CMPT_FIM", "COMPETEN"]
        linhas = [{c: r[c] for c in campos} for r in DBF(str(tmp / "x.dbf"), encoding="latin-1")]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return pd.DataFrame(linhas)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifesto = {"script": Path(__file__).name, "executado_em": dt.date.today().isoformat(),
                 "fonte": f"ftp://{HOST}{DIR}", "grupo": GRUPO, "competencias": [REF, FOLLOW], "arquivos": []}
    partes = []
    for comp in (REF, FOLLOW):
        aamm = str(comp)[2:]
        for uf in UFS:
            nome = f"HB{uf}{aamm}.dbc"
            b = baixar(nome)
            manifesto["arquivos"].append({"arquivo": nome, "bytes": len(b), "sha256": sha256(b)})
            df = ler_dbc(b)
            df["uf"] = uf
            df["vintage"] = comp
            partes.append(df)
    hb = pd.concat(partes, ignore_index=True)
    hb["CMPT_INI"] = pd.to_numeric(hb["CMPT_INI"], errors="coerce")
    # controle de coerencia: a vintage tem de ser a competencia declarada no proprio arquivo
    comp_arquivo = pd.to_numeric(hb["COMPETEN"], errors="coerce")
    assert (comp_arquivo == hb["vintage"]).all(), "COMPETEN diverge do nome do arquivo"
    p = hb[hb["SGRUPHAB"] == GRUPO].copy()
    p["co_ibge_6d"] = pd.to_numeric(p["CODUFMUN"], errors="coerce").astype("Int64")

    ref = set(p.loc[p["vintage"] == REF, "co_ibge_6d"].dropna().astype(int))
    novos = p[(p["vintage"] == FOLLOW) & (p["CMPT_INI"] > REF) & (p["CMPT_INI"] <= FOLLOW)]
    novo_mun = set(novos["co_ibge_6d"].dropna().astype(int))
    vig_follow = p[p["vintage"] == FOLLOW]
    n_cnes = vig_follow.groupby("co_ibge_6d")["CNES"].nunique()

    nacional = {
        "estabelecimentos_3801_vigentes_ref": int(p.loc[p["vintage"] == REF, "CNES"].nunique()),
        "estabelecimentos_3801_vigentes_follow": int(vig_follow["CNES"].nunique()),
        "municipios_3801_ref": len(ref),
        "municipios_3801_follow": int(vig_follow["co_ibge_6d"].nunique()),
        "municipios_com_3801_novo_na_janela": len(novo_mun),
        "cmpt_ini_dos_novos_por_mes": {str(int(k)): int(v) for k, v in novos.groupby("CMPT_INI")["CNES"].nunique().items()},
    }

    painel = pd.read_parquet(PAINEL)
    manifesto["painel_a5_sha256"] = sha256(PAINEL.read_bytes())
    cel = (painel[painel["amostra_confirmatoria"]]
           .groupby(["co_ibge_6d", "cod_curso"], as_index=False)
           .agg(atracao=("atracao_muni", "max"), sg_uf=("sg_uf", "first"),
                estrato=("estrato", "first"), log_pop=("log_pop", "first")))
    cel["co_ibge_6d"] = cel["co_ibge_6d"].astype(int)
    cel["pmae_vigente_ref"] = cel["co_ibge_6d"].isin(ref)
    cel["pmae_novo_janela"] = cel["co_ibge_6d"].isin(novo_mun)
    cel["pmae_entrada_janela"] = cel["pmae_novo_janela"] & ~cel["pmae_vigente_ref"]
    cel["n_cnes_3801_follow"] = cel["co_ibge_6d"].map(n_cnes).fillna(0).astype(int)

    def resumo(g: pd.DataFrame) -> dict:
        return {"celulas": int(len(g)), "municipios": int(g["co_ibge_6d"].nunique()),
                **{c: float(g[c].mean()) for c in ["pmae_vigente_ref", "pmae_novo_janela", "pmae_entrada_janela"]}}

    equilibrio = {"com_atracao": resumo(cel[cel["atracao"] == 1]), "sem_atracao": resumo(cel[cel["atracao"] == 0])}
    for c in ["pmae_vigente_ref", "pmae_novo_janela", "pmae_entrada_janela"]:
        equilibrio[f"diferenca_{c}"] = equilibrio["com_atracao"][c] - equilibrio["sem_atracao"][c]

    # inferencia por permutacao do rotulo de atracao entre municipios (o rotulo varia dentro do
    # municipio entre cursos, mas a exposicao e municipal, entao a permutacao e de celulas dentro de UF)
    import numpy as np
    rng = np.random.default_rng(20261014)
    perm = {}
    for c in ["pmae_novo_janela", "pmae_entrada_janela"]:
        obs = equilibrio[f"diferenca_{c}"]
        sims = []
        for _ in range(5000):
            a = cel.groupby("sg_uf")["atracao"].transform(lambda s: rng.permutation(s.to_numpy()))
            sims.append(cel.loc[a == 1, c].mean() - cel.loc[a == 0, c].mean())
        perm[c] = {"diferenca": obs, "p_bicaudal_permutacao_dentro_de_uf": float(np.mean(np.abs(sims) >= abs(obs)))}
    equilibrio["permutacao"] = perm

    # a diferenca bruta pode ser so porte: municipio maior atrai mais e recebe mais habilitacao.
    # MQO descritivo com estrato, log da populacao e UF, erro agrupado por municipio
    import statsmodels.formula.api as smf
    ajustado = {}
    for c in ["pmae_novo_janela", "pmae_entrada_janela"]:
        d = cel.assign(y=cel[c].astype(float))
        m = smf.ols("y ~ atracao + C(estrato) + log_pop + C(sg_uf)", data=d).fit(
            cov_type="cluster", cov_kwds={"groups": d["co_ibge_6d"]})
        ajustado[c] = {"coef_atracao": float(m.params["atracao"]), "ep": float(m.bse["atracao"]),
                       "p": float(m.pvalues["atracao"]), "n": int(m.nobs)}
    equilibrio["ajustado_estrato_porte_uf"] = ajustado

    resultado = {"protocolo": "A5_AMEACA_PMAE", "linguagem": "associativa; exposicao a ato administrativo concorrente",
                 "nacional": nacional, "amostra_a5_confirmatoria": equilibrio}
    cel.drop(columns=["sg_uf", "log_pop"]).to_csv(OUT / "A5_ameaca_pmae_celulas.csv", index=False)
    (OUT / "A5_ameaca_pmae.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "A5_ameaca_pmae_manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
