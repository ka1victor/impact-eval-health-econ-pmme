"""Arquiva a fonte bruta do IBGE (capitais, UF e região) usada pelo adendo 48c.

Motivo: achado A1 da auditoria 42 (`docs/auditorias/42_auditoria_capitais_uf.md`) e recomendação A8 da auditoria 40.
O modo `--baixar-referencias` de `scripts/rdd_bolsa/41_h1_capitais_uf.py` leu o ZIP do IBGE e as respostas do SIDRA
em memória, gravou só a cópia `output/aquisicao/ibge_capitais_uf_regiao.csv` e o manifesto
`output/aquisicao/manifesto_ibge_capitais_uf_regiao.json`. Sem a fonte arquivada, a cópia não se reproduz sem rede.
O autor autorizou baixar de novo e arquivar (26/10/2026).

Fontes (as mesmas URLs do manifesto do 41, lidas dele):
- IBGE, Localidades do Brasil 2022 (geoftp): ZIP com `BR_localidades_2022.dbf`; capitais = `CT_LOCALID == 'Cidade'`
  e `SCT_LOCALI` em 'Capital Estadual' / 'Capital Federal';
- IBGE, SIDRA, tabela 4709 (Censo 2022): níveis n2 (Grande Região) e n3 (UF por região), só para a pertença
  UF -> Grande Região.

Modos:
    python3 scripts/aquisicao/a19_arquivar_ibge_capitais_uf.py --baixar     # rede: baixa o que falta e arquiva
    python3 scripts/aquisicao/a19_arquivar_ibge_capitais_uf.py --verificar  # sem rede; não grava nada (padrão)

`--baixar`:
- baixa só os arquivos que ainda não estão arquivados; arquivo já arquivado com o SHA-256 do manifesto não é
  baixado de novo, e arquivo arquivado com outro hash faz o script parar sem tocar nele;
- SHA-256 igual ao do manifesto do 41: grava com o nome canônico em `data/raw/aquisicao/ibge_capitais_uf/`;
- SHA-256 diferente (o IBGE pode ter atualizado): não substitui nada; grava o bruto novo com a data no nome
  (`<nome>_baixado_AAAAMMDD.<ext>`), monta a tabela a partir dele e compara as 27 capitais, UF e região com a cópia
  atual. O pipeline não muda nesse caso;
- grava `output/aquisicao/a19_manifesto_arquivamento_ibge_capitais_uf.json` (fonte, URL, data de acesso, cobertura,
  unidade, chaves, tamanho e SHA-256 de cada bruto, e o resultado da reconstrução).

`--verificar`: lê só os brutos arquivados, confere o SHA-256 contra o manifesto do 41, reconstrói a tabela com a
mesma lógica do `--baixar-referencias` do 41 e confere que os bytes são iguais aos de
`output/aquisicao/ibge_capitais_uf_regiao.csv`. Não acessa a rede e não grava arquivo nenhum.

Nada aqui lê IVS, CNES ou outcome. Escreve só em `data/raw/aquisicao/ibge_capitais_uf/` (diretório novo) e em
`output/aquisicao/`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "aquisicao" / "ibge_capitais_uf"
OUT = ROOT / "output" / "aquisicao"
MANIFESTO_41 = OUT / "manifesto_ibge_capitais_uf_regiao.json"
REF_CSV = OUT / "ibge_capitais_uf_regiao.csv"
MANIFESTO_ARQ = OUT / "a19_manifesto_arquivamento_ibge_capitais_uf.json"

NATUREZA = "EMPIRICO"
ETAPA = "a19_arquivar_ibge_capitais_uf (scripts/aquisicao/a19_arquivar_ibge_capitais_uf.py)"
DBF_LOCALIDADES = "BR_localidades_2022.dbf"
CATEGORIA_CIDADE = "Cidade"
SUBCATEGORIAS_CAPITAL = ("Capital Estadual", "Capital Federal")
COLUNAS_REF = ["cd_uf", "sigla_uf", "nome_uf", "cd_regiao", "nome_regiao", "capital_co_ibge_7d",
               "capital_co_ibge_6d", "capital_nome", "categoria_ibge"]
REGIOES = {"Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"}


class FalhaValidacao(RuntimeError):
    pass


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rotulo(caminho: Path) -> str:
    p = Path(caminho).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Lista dos brutos, lida do manifesto do 41 (mesmas URLs, mesmos hashes)
# ---------------------------------------------------------------------------

def ler_manifesto_41() -> dict:
    if not MANIFESTO_41.exists():
        raise FalhaValidacao(f"manifesto do 41 ausente: {rotulo(MANIFESTO_41)}")
    return json.loads(MANIFESTO_41.read_text(encoding="utf-8"))


def brutos_esperados(man: dict) -> list[dict]:
    """Um item por arquivo bruto: papel, URL, nome canônico no arquivo e SHA-256 registrado pelo 41."""
    cap = man["fontes"]["capitais"]
    reg = man["fontes"]["regioes"]
    itens = [{"papel": "capitais", "regiao": None, "url": cap["url"], "nome": Path(cap["url"]).name,
              "sha256_esperado": cap["sha256_zip"], "fonte": cap["fonte"], "data_referencia": cap["data_referencia"],
              "cobertura": cap["cobertura"], "unidade": cap["unidade"], "chaves": cap["chaves"],
              "last_modified_manifesto": cap.get("last_modified")},
             {"papel": "regioes", "regiao": None, "url": reg["regioes"]["url"],
              "nome": "sidra_4709_n2_all_v93_p2022.json", "sha256_esperado": reg["regioes"]["sha256_resposta"],
              "fonte": reg["fonte"], "data_referencia": reg["data_referencia"], "cobertura": "5 Grandes Regiões",
              "unidade": "Grande Região", "chaves": reg["chaves"], "last_modified_manifesto": None}]
    for x in reg["ufs_por_regiao"]:
        itens.append({"papel": "ufs_por_regiao", "regiao": x["regiao"], "url": x["url"],
                      "nome": f"sidra_4709_n3_in_n2_{x['regiao']}_v93_p2022.json",
                      "sha256_esperado": x["sha256_resposta"], "fonte": reg["fonte"],
                      "data_referencia": reg["data_referencia"], "cobertura": f"UFs da Grande Região {x['regiao']}",
                      "unidade": "UF", "chaves": reg["chaves"], "last_modified_manifesto": None})
    return itens


def nome_datado(nome: str, data: str) -> str:
    p = Path(nome)
    return f"{p.stem}_baixado_{data.replace('-', '')}{p.suffix}"


# ---------------------------------------------------------------------------
# Reconstrução da tabela (mesma lógica de baixar_referencias() no 41, sem rede)
# ---------------------------------------------------------------------------

def capitais_do_zip(zbytes: bytes) -> tuple[pd.DataFrame, str, str]:
    from dbfread import DBF

    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        nomes = z.namelist()
        if DBF_LOCALIDADES not in nomes:
            raise FalhaValidacao(f"{DBF_LOCALIDADES} ausente do ZIP do IBGE ({nomes})")
        dbf_bytes = z.read(DBF_LOCALIDADES)
        cpg = DBF_LOCALIDADES.replace(".dbf", ".cpg")
        codificacao = z.read(cpg).decode("ascii").strip() if cpg in nomes else "utf-8"
    with tempfile.TemporaryDirectory() as tmp:
        caminho_dbf = Path(tmp) / DBF_LOCALIDADES
        caminho_dbf.write_bytes(dbf_bytes)
        linhas = [dict(r) for r in DBF(str(caminho_dbf), encoding=codificacao)
                  if r["CT_LOCALID"] == CATEGORIA_CIDADE and r["SCT_LOCALI"] in SUBCATEGORIAS_CAPITAL]
    cap = pd.DataFrame(linhas)
    if len(cap) != 27 or cap["CD_UF"].nunique() != 27:
        raise FalhaValidacao(f"esperadas 27 capitais, uma por UF; achadas {len(cap)} em {cap['CD_UF'].nunique()} UFs")
    if not (cap["CD_MUN"].str[:2] == cap["CD_UF"]).all():
        raise FalhaValidacao("capital com código de município fora da própria UF")
    return cap, sha256_bytes(dbf_bytes), codificacao


def montar_referencia(zbytes: bytes, regioes_bytes: bytes, ufs_bytes: dict[str, bytes]) -> pd.DataFrame:
    """Tabela das 27 UFs a partir dos brutos, como o --baixar-referencias do 41 a monta."""
    cap, _, _ = capitais_do_zip(zbytes)
    regioes = [(x["D1C"], x["D1N"]) for x in json.loads(regioes_bytes)]
    uf_reg = []
    for cod, nome in regioes:
        if cod not in ufs_bytes:
            raise FalhaValidacao(f"resposta do SIDRA das UFs da região {cod} ausente")
        uf_reg += [{"cd_uf": x["D1C"], "nome_uf_sidra": x["D1N"], "cd_regiao": cod, "nome_regiao": nome}
                   for x in json.loads(ufs_bytes[cod])]
    ur = pd.DataFrame(uf_reg)
    if len(ur) != 27 or ur["cd_uf"].nunique() != 27:
        raise FalhaValidacao("SIDRA não devolveu 27 UFs em 5 regiões")
    ref = cap.rename(columns={"CD_UF": "cd_uf", "SIGLA_UF": "sigla_uf", "NM_UF": "nome_uf",
                              "CD_MUN": "capital_co_ibge_7d", "NM_MUN": "capital_nome",
                              "SCT_LOCALI": "categoria_ibge"})[
        ["cd_uf", "sigla_uf", "nome_uf", "capital_co_ibge_7d", "capital_nome", "categoria_ibge"]]
    ref = ref.merge(ur, on="cd_uf", how="outer", validate="1:1", indicator=True)
    if (ref["_merge"] != "both").any():
        raise FalhaValidacao("UF sem capital ou sem região")
    if (ref["nome_uf"] != ref["nome_uf_sidra"]).any():
        raise FalhaValidacao("nome da UF difere entre Localidades 2022 e SIDRA")
    ref["capital_co_ibge_6d"] = ref["capital_co_ibge_7d"].str[:6]
    ref = ref[COLUNAS_REF].sort_values("cd_uf").reset_index(drop=True)
    if set(ref["nome_regiao"]) != REGIOES:
        raise FalhaValidacao("regiões reconstruídas não são as 5 Grandes Regiões")
    ref["natureza_dos_dados"] = NATUREZA
    return ref


def csv_bytes(ref: pd.DataFrame) -> bytes:
    return ref.to_csv(index=False, lineterminator="\n").encode("utf-8")


def comparar_conteudo(ref_nova: pd.DataFrame, ref_atual: pd.DataFrame) -> list[dict]:
    """Diferenças por UF nas colunas de conteúdo (27 capitais, UF, região) entre a tabela nova e a cópia atual."""
    a = ref_nova[COLUNAS_REF].astype(str).set_index("cd_uf")
    b = ref_atual[COLUNAS_REF].astype(str).set_index("cd_uf")
    difs = []
    for uf in sorted(set(a.index) | set(b.index)):
        if uf not in a.index or uf not in b.index:
            difs.append({"cd_uf": uf, "coluna": "(linha)", "atual": "presente" if uf in b.index else "ausente",
                         "novo": "presente" if uf in a.index else "ausente"})
            continue
        for col in COLUNAS_REF[1:]:
            if a.at[uf, col] != b.at[uf, col]:
                difs.append({"cd_uf": uf, "coluna": col, "atual": b.at[uf, col], "novo": a.at[uf, col]})
    return difs


# ---------------------------------------------------------------------------
# Verificação sem rede
# ---------------------------------------------------------------------------

def ler_brutos_arquivados(itens: list[dict]) -> dict[str, bytes]:
    """Bytes dos brutos com nome canônico; levanta erro se faltar algum ou se o SHA-256 não bater."""
    lidos = {}
    for it in itens:
        p = RAW / it["nome"]
        if not p.exists():
            raise FalhaValidacao(f"bruto não arquivado: {rotulo(p)}")
        b = p.read_bytes()
        if sha256_bytes(b) != it["sha256_esperado"]:
            raise FalhaValidacao(f"SHA-256 de {rotulo(p)} difere do manifesto do 41")
        lidos[it["nome"]] = b
    return lidos


def _bytes_para_montar(itens: list[dict], lidos: dict[str, bytes]) -> tuple[bytes, bytes, dict[str, bytes]]:
    z = next(lidos[it["nome"]] for it in itens if it["papel"] == "capitais")
    r = next(lidos[it["nome"]] for it in itens if it["papel"] == "regioes")
    u = {it["regiao"]: lidos[it["nome"]] for it in itens if it["papel"] == "ufs_por_regiao"}
    return z, r, u


def verificar() -> dict:
    """Reconstrói a cópia a partir do bruto arquivado, sem rede e sem gravar nada."""
    man = ler_manifesto_41()
    itens = brutos_esperados(man)
    lidos = ler_brutos_arquivados(itens)
    z, r, u = _bytes_para_montar(itens, lidos)
    _, sha_dbf, codificacao = capitais_do_zip(z)
    if sha_dbf != man["fontes"]["capitais"]["sha256_dbf"]:
        raise FalhaValidacao("SHA-256 do DBF extraído difere do manifesto do 41")
    if codificacao != man["fontes"]["capitais"]["codificacao"]:
        raise FalhaValidacao("codificação do DBF difere do manifesto do 41")
    reconstruido = csv_bytes(montar_referencia(z, r, u))
    atual = REF_CSV.read_bytes()
    res = {"csv": rotulo(REF_CSV), "sha256_csv_atual": sha256_bytes(atual),
           "sha256_csv_manifesto_41": man["saida"]["sha256"], "sha256_reconstruido": sha256_bytes(reconstruido),
           "linhas": 27, "sha256_dbf": sha_dbf, "identico": reconstruido == atual}
    if not res["identico"]:
        raise FalhaValidacao("a tabela reconstruída do bruto arquivado difere de "
                             f"{rotulo(REF_CSV)}: {res['sha256_reconstruido']} != {res['sha256_csv_atual']}")
    if res["sha256_reconstruido"] != man["saida"]["sha256"]:
        raise FalhaValidacao("a tabela reconstruída difere do SHA-256 registrado no manifesto do 41")
    return res


# ---------------------------------------------------------------------------
# Download e arquivamento
# ---------------------------------------------------------------------------

def _baixar(url: str, timeout: int = 300) -> tuple[bytes, dict]:
    with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310 (URLs fixas do IBGE, do manifesto do 41)
        corpo = r.read()
        cab = {k: r.headers.get(k) for k in ("Last-Modified", "Content-Length", "Content-Type")}
    return corpo, cab


def _gravar_novo(caminho: Path, b: bytes) -> None:
    """Grava só arquivo novo; arquivo existente com outros bytes nunca é substituído."""
    if caminho.exists():
        if caminho.read_bytes() != b:
            raise FalhaValidacao(f"{rotulo(caminho)} já existe com outro conteúdo; nada foi substituído")
        return
    parte = caminho.with_name(caminho.name + ".part")
    parte.write_bytes(b)
    parte.replace(caminho)


def arquivar() -> dict:
    man = ler_manifesto_41()
    itens = brutos_esperados(man)
    anterior = json.loads(MANIFESTO_ARQ.read_text(encoding="utf-8")) if MANIFESTO_ARQ.exists() else {}
    acessos_anteriores = {a["nome_canonico"]: a for a in anterior.get("arquivos", [])}
    RAW.mkdir(parents=True, exist_ok=True)
    agora = dt.datetime.now(dt.timezone.utc)
    acesso, data = agora.strftime("%Y-%m-%dT%H:%M:%SZ"), agora.strftime("%Y-%m-%d")

    registros, bytes_novos = [], {}
    for it in itens:
        canonico = RAW / it["nome"]
        if canonico.exists():
            b = canonico.read_bytes()
            if sha256_bytes(b) != it["sha256_esperado"]:
                raise FalhaValidacao(f"{rotulo(canonico)} já arquivado com SHA-256 diferente do manifesto; "
                                     "nada foi substituído")
            prev = acessos_anteriores.get(it["nome"], {})
            reg = {"data_acesso_utc": prev.get("data_acesso_utc"), "last_modified": prev.get("last_modified")}
            destino, confere = canonico, True
        else:
            b, cab = _baixar(it["url"], timeout=300 if it["papel"] == "capitais" else 60)
            confere = sha256_bytes(b) == it["sha256_esperado"]
            destino = canonico if confere else RAW / nome_datado(it["nome"], data)
            _gravar_novo(destino, b)
            reg = {"data_acesso_utc": acesso, "last_modified": cab.get("Last-Modified")}
            if not confere:
                bytes_novos[it["nome"]] = b
        registros.append({
            "papel": it["papel"], "regiao": it["regiao"], "fonte": it["fonte"], "url": it["url"],
            "nome_canonico": it["nome"], "arquivo": rotulo(destino), "bytes": len(b), "sha256": sha256_bytes(b),
            "sha256_manifesto_41": it["sha256_esperado"], "confere_com_manifesto_41": confere,
            "last_modified_manifesto_41": it["last_modified_manifesto"], **reg,
            "data_referencia": it["data_referencia"], "cobertura": it["cobertura"], "unidade": it["unidade"],
            "chaves": it["chaves"]})

    saida = {
        "natureza_dos_dados": NATUREZA,
        "etapa": ETAPA,
        "motivo": "achado A1 da auditoria 42 e recomendação A8 da auditoria 40: arquivar a fonte bruta do IBGE da "
                  "referência de capitais, UF e região do adendo 48c; download autorizado pelo autor em 26/10/2026",
        "manifesto_original": {"arquivo": rotulo(MANIFESTO_41), "sha256": sha256(MANIFESTO_41),
                               "data_acesso_utc": man["data_acesso_utc"]},
        "diretorio_bruto": rotulo(RAW),
        "filtro_capitais": f"CT_LOCALID == '{CATEGORIA_CIDADE}' e SCT_LOCALI em {list(SUBCATEGORIAS_CAPITAL)}",
        "uso_sidra": "só a pertença territorial UF -> Grande Região; o valor da variável 93 não é usado",
        "arquivos": registros,
    }
    if not bytes_novos:
        saida["situacao"] = "HASH_CONFERE"
        saida["reconstrucao_sem_rede"] = verificar()
        saida["pipeline"] = "inalterado: a cópia do 41 se reconstrói byte a byte do bruto arquivado"
    else:
        saida["situacao"] = "HASH_DIVERGE"
        # Bruto novo onde o hash divergiu; nos demais, o canônico já conferido.
        lidos = {}
        for it in itens:
            if it["nome"] in bytes_novos:
                lidos[it["nome"]] = bytes_novos[it["nome"]]
            elif (RAW / it["nome"]).exists():
                lidos[it["nome"]] = (RAW / it["nome"]).read_bytes()
            else:
                lidos[it["nome"]] = None
        faltam = [k for k, v in lidos.items() if v is None]
        if faltam:
            saida["comparacao_conteudo"] = {"executada": False, "motivo": f"brutos ausentes: {faltam}"}
        else:
            z, r, u = _bytes_para_montar(itens, lidos)
            ref_nova = montar_referencia(z, r, u)
            difs = comparar_conteudo(ref_nova, pd.read_csv(REF_CSV, dtype=str))
            saida["comparacao_conteudo"] = {
                "executada": True, "colunas": COLUNAS_REF, "n_diferencas": len(difs), "diferencas": difs,
                "sha256_tabela_nova": sha256_bytes(csv_bytes(ref_nova)), "sha256_csv_atual": sha256(REF_CSV)}
        saida["pipeline"] = ("inalterado: nada foi substituído; o bruto novo ficou com data no nome e a cópia do 41 "
                             "continua a do manifesto original")
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFESTO_ARQ.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return saida


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--baixar", action="store_true", help="baixa o que falta (rede) e arquiva")
    g.add_argument("--verificar", action="store_true", help="reconstrói a cópia do bruto arquivado (sem rede)")
    args = ap.parse_args(argv)
    if args.baixar:
        s = arquivar()
        print(f"situação: {s['situacao']}")
        for a in s["arquivos"]:
            print(f"  {a['arquivo']}: {a['bytes']} bytes, sha256 {a['sha256'][:12]}..., "
                  f"confere={a['confere_com_manifesto_41']}")
        if s["situacao"] == "HASH_DIVERGE":
            print(f"  diferenças de conteúdo: {s.get('comparacao_conteudo')}")
        print(f"manifesto: {rotulo(MANIFESTO_ARQ)}")
        return 0
    r = verificar()
    print(f"reconstrução sem rede de {r['csv']}: idêntica={r['identico']} (sha256 {r['sha256_reconstruido']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
