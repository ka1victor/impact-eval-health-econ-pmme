"""Resumo de 1 a 3 páginas para os professores: troca de "% de vagas preenchidas" por "nº de vagas preenchidas".

Resume a família N (protocolo 48, resultados em `docs/06_execucao/49_resultados_contagem_vagas_preenchidas.md`).
Não estima nada, não lê `data/` e não traz número digitado: toda cifra do texto, da tabela e da robustez é lida de
`output/rdd_bolsa/N_estimativas.csv`, `NA_estimativas.csv` e `N_resumo.json` e formatada aqui. A figura é a PNG gravada
pelo pipeline (`scripts/rdd_bolsa/23_estimar_contagem_vagas.py`), incorporada sem alteração. O estilo e o PDF vêm do
`gerar_figuras_validacao_professores.py`. O HTML não leva data nem commit (saída determinística).

Saídas:
- output/apresentacao_validacao/resumo_contagem_vagas.html
- output/apresentacao_validacao/resumo_contagem_vagas.pdf  (A4, Chromium headless)
"""

from __future__ import annotations

import base64
import importlib.util
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "output" / "apresentacao_validacao"
SAIDA_HTML = PASTA / "resumo_contagem_vagas.html"
SAIDA_PDF = PASTA / "resumo_contagem_vagas.pdf"
N_EST = ROOT / "output" / "rdd_bolsa" / "N_estimativas.csv"
NA_EST = ROOT / "output" / "rdd_bolsa" / "NA_estimativas.csv"
N_RES = ROOT / "output" / "rdd_bolsa" / "N_resumo.json"
FIGURA = ROOT / "output" / "rdd_bolsa" / "N_figuras" / "N1_com_controle_empilhado.png"


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


FIG = _carregar("figuras_professores_base", ROOT / "scripts" / "apresentacao" / "gerar_figuras_validacao_professores.py")
_fmt, _num = FIG._fmt, FIG._num


def _p(x: float) -> str:
    return "< 0,001" if x < 0.001 else _num(x, 3)


def _ic(inf: float, sup: float) -> str:
    return f"[{_fmt(inf, 2)}; {_fmt(sup, 2)}]"


def _cs(x) -> str:
    return f"{float(x):.3f}".replace(".", ",")


# Rótulo de cada outcome da família N (sem número de resultado).
ROTULOS = {"N1": "N1 · vagas preenchidas na 1ª chamada",
           "N2": "N2 · células (estabelecimento × curso) com alocado na 1ª chamada",
           "N3": "N3 · células com alocado até a 2ª chamada",
           "N4": "N4 · especialistas ativos do ciclo"}


def _ciclos(c: str) -> str:
    v = str(c).split("+")
    return v[0] if len(v) == 1 else f"{v[0]} a {v[-1]}"


def _empilhada(n: pd.DataFrame, oid: str, esp: str) -> pd.Series:
    """Linha principal, h do protocolo, cortes empilhados, na maior população empilhada do outcome."""
    d = n[(n["outcome_id"] == oid) & (n["especificacao"] == esp) & (n["variante"] == "principal")
          & (n["corte"].astype(str) == "empilhado") & (n["populacao"].str.contains(r"\+"))].copy()
    d["k"] = d["populacao"].str.count(r"\+")
    d = d[d["k"] == d["k"].max()]
    if len(d) != 1:
        raise SystemExit(f"linha empilhada ausente ou duplicada: {oid} {esp}")
    return d.iloc[0]


def _dados() -> dict:
    n = pd.read_csv(N_EST)
    na = pd.read_csv(NA_EST)
    res = json.loads(N_RES.read_text(encoding="utf-8"))
    princ = n[(n["variante"] == "principal") & (n["especificacao"] == "S-a")]
    h = float(princ["h"].iloc[0])
    cortes = sorted({float(c) for c in princ["corte"].astype(str) if re.fullmatch(r"\d\.\d+", c)})
    ciclos = sorted({c for c in princ["populacao"].str.extract(r"^V(\d)$")[0].dropna()})
    linhas = {(o, e): _empilhada(n, o, e) for o in ROTULOS for e in ("S-a", "S-b")}
    return dict(n=n, na=na, res=res, h=h, cortes=cortes, ciclos=ciclos, linhas=linhas)


def _tabela(d: dict) -> str:
    corpo = ""
    for oid, rot in ROTULOS.items():
        for esp, nome in (("S-a", "com controle"), ("S-b", "sem controle")):
            r = d["linhas"][(oid, esp)]
            holm = _num(r["p_holm"], 3) if pd.notna(r["p_holm"]) else "—"
            exclui = not (r["ic95_inf"] <= 0 <= r["ic95_sup"])
            corpo += (f"<tr><td class='txt'>{rot if esp == 'S-a' else ''}</td><td class='txt'>{nome}</td>"
                      f"<td>{_ciclos(r['ciclo']) if esp == 'S-a' else ''}</td>"
                      f"<td>{int(r['n_abaixo'])} / {int(r['n_acima'])}</td><td class='num'>{_num(r['media_abaixo'])}</td>"
                      f"<td class='num'><b>{_fmt(r['tau'], 2)}</b></td>"
                      f"<td class='num{' sig' if exclui else ''}'>{_ic(r['ic95_inf'], r['ic95_sup'])}</td>"
                      f"<td class='num'>{_p(r['p_valor'])}</td><td class='num'>{holm}</td>"
                      f"<td class='num'>{_num(r['mde'])}</td></tr>")
    return ('<table class="res compacta"><thead><tr><th>Outcome</th><th>Especificação</th><th>Ciclos</th>'
            '<th>Municípios abaixo / acima</th><th>Média abaixo</th><th>Salto</th><th>IC 95%</th><th>p</th>'
            f'<th>p Holm</th><th>MDE</th></tr></thead><tbody>{corpo}</tbody></table>')


def _leitura_tabela(d: dict) -> str:
    a = [d["linhas"][(o, "S-a")] for o in ROTULOS]
    b = [d["linhas"][(o, "S-b")] for o in ROTULOS]
    if not all(r["tau"] < 0 for r in a + b):
        raise SystemExit("o texto supõe saltos empilhados todos negativos; revisar")
    if not all(r["p_holm"] >= 0.05 for r in a):
        raise SystemExit("o texto supõe que nenhuma S-a sobrevive ao Holm; revisar")
    sem = [o for o, r in zip(ROTULOS, b) if not (r["ic95_inf"] <= 0 <= r["ic95_sup"])]
    com = [o for o, r in zip(ROTULOS, a) if not (r["ic95_inf"] <= 0 <= r["ic95_sup"])]
    return (f"Todos os saltos empilhados são <b>negativos</b>: não há aumento de vagas preenchidas do lado com bolsa "
            f"maior. Com controle, o IC 95% exclui zero em {', '.join(com)}; sem controle, em {', '.join(sem)}. "
            "Depois da correção de Holm entre as quatro linhas com controle, nenhuma rejeita zero. Os demais ICs "
            "incluem zero.")


def _como_ler_fig(d: dict) -> str:
    return ("<b>Como ler.</b> Cada bolinha é a média de vagas preenchidas (já ajustada pelas vagas oferecidas) dos "
            "municípios de uma faixa estreita de IVS; o tamanho indica quantas observações há na faixa. Azul: dentro "
            f"da janela usada na estimação (até {_cs(d['h'])} do corte); cinza: fora, só contexto. As <b>retas</b> são "
            "ajustadas separadamente de cada lado do corte e a <b>faixa clara</b> é o IC 95% da reta. A <b>seta "
            "laranja</b> é o salto no corte, isto é, o efeito estimado (lado de bolsa maior menos lado de bolsa menor); "
            "valor, IC e p estão no título. Ciclos e cortes aparecem juntos: o eixo horizontal é a distância ao corte.")


def _robustez(d: dict) -> str:
    res, na = d["res"], d["na"]
    sens = next(x for x in res["sensibilidade_coeficiente_unico_auditoria_20"]["linhas"] if x["outcome_id"] == "N1")
    r_sc = res["veredito_S_c"]
    pl = next(x for x in res["placebos_grade"] if x["outcome_id"] == "N1" and x["ciclo"] == "2"
              and x["especificacao"] == "S-a" and x["corte"] == "0.300")
    n = d["n"]
    seg = n[(n["outcome_id"] == "N1") & (n["populacao"] == "V2") & (n["especificacao"] == "S-i")
            & (n["variante"] == "media_do_segmento_entre_0,300_e_0,400 (S-b)")]
    if len(seg) != 1:
        raise SystemExit("placebo por segmento do ciclo 2 ausente")
    seg = seg.iloc[0]
    emp = na[(na["corte"].astype(str) == "empilhado") & (na["ciclo"] == "1+2+3") & (na["variante"] == "com_covariaveis")
             & (na["outcome_id"] == "N1")].iloc[0]
    emp_u = na[(na["corte"].astype(str) == "empilhado") & (na["ciclo"] == "1+2+3")
               & (na["variante"] == "com_covariaveis_coeficiente_unico") & (na["outcome_id"] == "N1")].iloc[0]
    a1 = na[(na["corte"].astype(str) == "empilhado") & (na["ciclo"] == "1+2+3") & (na["variante"] == "principal")
            & (na["outcome_id"] == "A1_PREENCH_10K") & (na["especificacao"] == "A1")].iloc[0]
    passa = sens["p_holm_coef_unico"] < 0.05
    quais = r_sc["quais"]
    itens = [
        ("Coeficiente único do controle.",
         f"Se o controle tiver um só coeficiente para todos os ciclos e cortes (fora do protocolo), o salto de N1 é "
         f"{_fmt(sens['tau_coef_unico'], 2)} vaga, IC 95% {_ic(sens['ic95_inf_coef_unico'], sens['ic95_sup_coef_unico'])}, "
         f"p Holm = {_num(sens['p_holm_coef_unico'], 3)}: {'passa' if passa else 'não passa'} no Holm. O teste de "
         f"Wald rejeita coeficientes iguais (p {_p(sens['wald_igualdade_p'])}) e o protocolo usa um por ciclo × corte; "
         "a conclusão do Holm depende dessa escolha, então a leitura é &ldquo;negativo, frágil&rdquo;."),
        ("Oferta como outcome (S-c).",
         f"Em {r_sc['n_p_menor_005']} de {r_sc['n_linhas']} linhas as vagas oferecidas saltam no corte ({quais}); "
         f"empilhado, {_fmt(r_sc['tau_empilhado'], 2)} vaga, p = {_num(r_sc['p_empilhado'], 3)}. É o motivo de "
         "reportar as duas leituras."),
        ("Covariáveis pré-determinadas (A4).",
         f"Sem covariáveis, na mesma amostra, o salto de N1 é {_fmt(emp_sem(na)['tau'], 2)}; com o log da população e os "
         f"estoques de especialistas do CNES pré-programa, {_fmt(emp['tau'], 2)}, IC 95% "
         f"{_ic(emp['ic95_inf'], emp['ic95_sup'])}, p = {_num(emp['p_valor'], 3)}. Com um só coeficiente para as "
         f"covariáveis, {_fmt(emp_u['tau'], 2)}, IC {_ic(emp_u['ic95_inf'], emp_u['ic95_sup'])}. Compatível com "
         "diferenças de porte entre os lados do corte, mas não as demonstra."),
        ("Por habitante (A1).",
         f"Vagas preenchidas por 10 mil habitantes, todos os municípios (zero fora do quadro): salto de "
         f"{_fmt(a1['tau'], 3)}, IC 95% {_ic3(a1['ic95_inf'], a1['ic95_sup'])}, p = {_num(a1['p_valor'], 3)}. "
         "O IC inclui zero."),
        ("Placebo do ciclo 2.",
         f"Com controle, o corte {_cs(float(pl['corte']))} do ciclo 2 tem t = {_fmt(pl['t_real'], 2)}, mais extremo que "
         f"{'todos os' if pl['n_abs_t_placebo_maior_ou_igual_ao_real'] == 0 else 'parte dos'} {pl['n_placebos']} cortes "
         f"falsos da grade (p por posto = {_num(pl['p_posto'], 3)}); mas sem controle, um corte falso entre os dois "
         f"cortes reais tem salto {_fmt(seg['tau'], 2)}, IC 95% {_ic(seg['ic95_inf'], seg['ic95_sup'])}. Isso põe "
         "em dúvida a reta local do ciclo 2 em torno do corte inferior."),
    ]
    return "<ul class='rob'>" + "".join(f"<li><b>{t}</b> {x}</li>" for t, x in itens) + "</ul>"


def _ic3(inf: float, sup: float) -> str:
    return f"[{_fmt(inf, 3)}; {_fmt(sup, 3)}]"


def emp_sem(na: pd.DataFrame) -> pd.Series:
    return na[(na["corte"].astype(str) == "empilhado") & (na["ciclo"] == "1+2+3") & (na["outcome_id"] == "N1")
              & (na["variante"] == "sem_covariaveis_mesma_amostra")].iloc[0]


CSS_EXTRA = """
@page { size: A4 portrait; margin: 12mm 14mm;
  @bottom-left { content: "Resumo para os professores · família N (contagem de vagas preenchidas)"; } }
main { max-width: 182mm; }
body { font-size: 10pt; }
h1 { font-size: 17pt; margin: 0 0 1mm; }
.sub { color: var(--ink2); font-size: 9.5pt; margin: 0 0 3mm; }
h2 { font-size: 11.5pt; margin: 4mm 0 1.5mm; border: 0; }
p, li { line-height: 1.38; margin: 0 0 1.6mm; }
ul.rob { padding-left: 4.5mm; margin: 0; } ul.rob li { margin-bottom: 1.4mm; }
table.res { width: 100%; border-collapse: collapse; font-size: 8pt; margin: 2mm 0; }
table.res th, table.res td { padding: 1.1mm 1.2mm; border-bottom: 1px solid var(--grid); text-align: center; }
table.res th { background: var(--wash); font-weight: 650; } table.res td.txt { text-align: left; }
td.sig { font-weight: 650; }
.nota { font-size: 8pt; color: var(--muted); margin: 1mm 0 2mm; }
.caixa { background: var(--wash); border-radius: 5px; padding: 2.5mm 3mm; font-size: 9.2pt; margin: 2mm 0; }
.fig-img { display: block; margin: 0 auto; max-width: 100%; max-height: 98mm; width: auto; }
.quebra { break-before: page; }
.conc { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.conc ul { margin: 0; padding-left: 4.5mm; }
section { break-inside: avoid; }
"""


def montar_html() -> str:
    d = _dados()
    origem = (PASTA / "relatorio_validacao_rdd_bolsa.html").read_text(encoding="utf-8")
    estilo = re.search(r"<style>.*?</style>", origem, re.S).group(0).replace("</style>", CSS_EXTRA + "</style>")
    contraste = d["res"]["contraste"]
    degrau = re.search(r"R\$ \d+ mil", contraste).group(0)
    cortes = " e ".join(_cs(c) for c in d["cortes"])
    ciclos = f"{d['ciclos'][0]}–{d['ciclos'][-1]}"
    quais = d["res"]["veredito_S_c"]["quais"]
    png = base64.b64encode(FIGURA.read_bytes()).decode("ascii")

    s1 = ("<section><h2>1. O que mudou</h2>"
          "<p>O efeito deixa de ser a <b>fração</b> das vagas preenchidas e passa a ser o <b>número de vagas "
          "preenchidas na 1ª chamada</b> por município (N1), como os professores sugeriram. Mostramos duas leituras: "
          "<b>sem controle</b>, o efeito total da faixa sobre o número de vagas preenchidas; e <b>com controle</b> "
          "pelo número de vagas oferecidas, que lê o preenchimento <i>dado</i> o que foi oferecido.</p>"
          "<p><b>Por que o controle exige cuidado:</b> numa RDD ele não é necessário para identificar o efeito; só "
          "reduz variância se for pré-determinado. As vagas oferecidas são definidas por gestor e SGTES e podem "
          f"responder ao corte. Testamos isso (S-c): a oferta salta em parte das amostras ({quais}). Então a linha com "
          "controle é condicional à oferta, e a linha sem controle inclui a resposta da oferta.</p></section>")
    s2 = ("<section><h2>2. Desenho em três linhas</h2><ul>"
          f"<li>RDD local linear <i>sharp</i>, kernel triangular, running variable = IVS 2010 oficial do Ipea, cortes em "
          f"{cortes}, janela h = {_cs(d['h'])}.</li>"
          f"<li>Ciclos {ciclos} e os dois cortes empilhados (intercepto e inclinação por ciclo × corte, salto comum); "
          "erro-padrão agrupado por município. Salto = lado de bolsa maior menos lado de bolsa menor.</li>"
          f"<li><b>O que o contraste mede:</b> o pacote do corte (o degrau de {degrau} por mês na bolsa anunciada mais "
          "outras regras federais que mudam nos mesmos cortes). Não é o degrau isolado nem a participação no "
          "PMM-E.</li></ul></section>")
    s3 = ("<section><h2>3. Resultado principal: N1 a N4, ciclos e cortes empilhados</h2>" + _tabela(d) +
          "<p class='nota'>Salto em unidades do outcome (vagas, células ou especialistas por município). Média abaixo = "
          "média do outcome no lado de bolsa menor, dentro da janela. MDE = efeito mínimo detectável do protocolo. Holm só entre as quatro linhas "
          "com controle. IC em negrito = exclui zero. Fonte: <code>output/rdd_bolsa/N_estimativas.csv</code>; "
          "protocolo 48.</p>"
          f"<div class='caixa'><b>O que mostra.</b> {_leitura_tabela(d)}</div></section>")
    s4 = ("<section class='quebra'><h2>4. O resultado de N1 em gráfico</h2>"
          f"<img class='fig-img' src='data:image/png;base64,{png}' alt='RDD de N1 com controle, empilhado'>"
          "<p class='nota'>Fonte: <code>output/rdd_bolsa/N_figuras/N1_com_controle_empilhado.png</code>, gravada por "
          "<code>scripts/rdd_bolsa/23_estimar_contagem_vagas.py</code> e incorporada sem alteração. A versão sem "
          "controle está na mesma pasta.</p>"
          f"<div class='caixa'>{_como_ler_fig(d)}</div></section>")
    s5 = f"<section><h2>5. Robustez</h2>{_robustez(d)}</section>"
    s6 = ("<section><h2>6. O que se pode e o que não se pode afirmar</h2><div class='conc'><div><b>Pode-se afirmar "
          "(descrição, com a precisão relatada)</b><ul>"
          f"<li>Trocar a fração pelo número de vagas preenchidas, com ou sem controle, não faz aparecer efeito "
          f"positivo do degrau de {degrau}.</li>"
          "<li>As estimativas empilhadas são negativas, mas nenhuma sobrevive ao Holm na especificação do protocolo; "
          "o resultado depende do coeficiente do controle.</li>"
          "<li>O controle não é inócuo: a oferta salta em parte das amostras, e a estimativa com controle é "
          "condicional a ela.</li></ul></div><div><b>Não se pode afirmar</b><ul>"
          "<li>Que a bolsa reduz o preenchimento: o pacote do corte inclui outras regras, o Holm não descarta zero e o "
          "placebo do ciclo 2 põe em dúvida a reta local.</li>"
          "<li>Que o salto com controle seja o preenchimento causal por vaga, se a oferta respondeu à faixa.</li>"
          "<li>Nada sobre participação no PMM-E, sobre o Agora Tem Especialistas ou sobre retenção individual.</li>"
          "<li>Falta de evidência não é prova de efeito nulo: há poucas dezenas de municípios por lado.</li>"
          "</ul></div></div></section>")
    return ('<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Contagem de vagas preenchidas: resumo</title>{estilo}</head><body><main>'
            '<h1>Nº de vagas preenchidas como variável de efeito</h1>'
            '<p class="sub">RDD do adicional da bolsa do PMM-E · família N (protocolo 48) · resumo para os '
            f'professores</p>{s1}{s2}{s3}{s4}{s5}{s6}</main></body></html>\n')


def main() -> None:
    SAIDA_HTML.write_text(montar_html(), encoding="utf-8")
    FIG._imprimir_pdf(SAIDA_HTML, SAIDA_PDF)
    print(f"gravado: {SAIDA_HTML.relative_to(ROOT)} e {SAIDA_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
