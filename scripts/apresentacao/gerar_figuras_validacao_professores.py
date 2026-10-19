"""Versão só com figuras do relatório de validação para os professores.

Lê as figuras já gravadas em
`output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.html` (gerado por
`gerar_relatorio_validacao_professores.py`) e troca o subtítulo de cada uma por
uma explicação curta e qualitativa. Não estima nada, não lê `data/` e não traz
número novo: os números que aparecem nas figuras e nos títulos vêm do relatório
de origem, que os lê de `output/`.

Saídas:
- output/apresentacao_validacao/figuras_validacao_rdd_bolsa.html
- output/apresentacao_validacao/figuras_validacao_rdd_bolsa.pdf  (A4, Chromium headless)
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "output" / "apresentacao_validacao"
ORIGEM = PASTA / "relatorio_validacao_rdd_bolsa.html"
SAIDA_HTML = PASTA / "figuras_validacao_rdd_bolsa.html"
SAIDA_PDF = PASTA / "figuras_validacao_rdd_bolsa.pdf"

# Explicação curta por figura, na ordem do relatório de origem. Sem números.
EXPLICACOES = [
    "A regra da bolsa. Cada ponto é um município; a bolsa sobe em degrau exatamente nos cortes de IVS. "
    "É isso que torna a comparação \"logo abaixo × logo acima do corte\" possível.",
    "Teste de manipulação. Se os municípios conseguissem ajustar o IVS para ganhar a bolsa maior, haveria "
    "acúmulo logo acima do corte. As barras seguem a contagem esperada: não há sinal de manipulação.",
    "O resultado principal com o outcome original (preenchimento das vagas). Cada ponto é a média de uma faixa "
    "de IVS; as retas são ajustadas de cada lado do corte. O efeito é o degrau entre as retas no corte. "
    "O degrau é pequeno diante da faixa sombreada (IC 95%): resultado inconclusivo.",
    "Índice que junta atração, preenchimento e presença, com ciclos e cortes agrupados. Não aparece degrau "
    "no corte.",
    "Replicação no ciclo 2 do resultado de preenchimento: mesma leitura, sem degrau distinguível de zero.",
    "O mesmo no ciclo 3 (ainda incompleto): sem degrau distinguível de zero.",
    "Oferta de especialistas no CNES (vínculos por 10 mil habitantes), antes e depois do programa. "
    "O degrau no nível mistura a bolsa com outras políticas que mudam nos mesmos cortes.",
    "Por isso usamos a diferença em descontinuidades: o degrau na variação (pós − pré). "
    "Ela remove o que outras políticas já faziam antes do programa. Sem degrau distinguível de zero.",
    "Estudo de evento: o degrau mês a mês. Antes do programa deveria ser plano; a área à direita é o "
    "período depois da entrada dos especialistas. Em 0,300 já havia degrau antes do programa, por isso o "
    "nível não serve e a variação é a referência. Não há mudança clara depois da entrada.",
    "Escolha dos candidatos: quanto cada vaga atrai, conforme o IVS. O salto nos cortes mostra que, "
    "no ciclo 2, candidatos preferem a vaga com bolsa maior. É o único sinal robusto.",
    "O que os dados permitem descartar. Cada linha é um resultado com seu IC 95%; quando o IC não "
    "alcança a referência do protocolo, um efeito desse tamanho fica descartado. Em geral, o poder é baixo.",
]


# Mínimo para dar a ideia do método e dos resultados: regra, manipulação, RDD tradicional e DiRD (posições em EXPLICACOES).
# Na versão só de método, estas legendas substituem as de EXPLICACOES.
SELECIONADAS = (0, 1, 2, 7)


# Versão lean: cada página é um passo da lógica (título-afirmação + figura + uma ou duas linhas).
PASSOS = {
    0: ("1. A regra cria um experimento",
        "<b>Como ler:</b> cada bolinha é um município, posicionado pelo seu IVS (eixo horizontal) e pela bolsa "
        "anunciada para ele (eixo vertical). A bolsa sobe R$ 5 mil, de forma automática, exatamente em 0,300 e em "
        "0,400. Municípios logo abaixo e logo acima do corte são parecidos; só a bolsa muda."),
    1: ("2. Ninguém escolheu o lado do corte",
        "<b>Como ler:</b> cada barra conta quantos municípios têm IVS numa faixa estreita (largura 0,005). Barras "
        "azuis estão dentro da janela usada na estimação; cinzas, fora. A linha preta é a contagem esperada se "
        "ninguém se amontoasse logo acima do corte para ganhar a bolsa maior. As barras seguem a linha: sem "
        "manipulação. O IVS vem do Censo 2010, anterior ao programa."),
    2: ("4. O resultado em gráfico: o degrau no corte",
        "<b>Como ler:</b> um painel por corte; eixo horizontal = IVS; eixo vertical = fração das vagas preenchidas "
        "no município. <b>Bolinhas</b> = média dessa fração entre os municípios de uma faixa estreita de IVS "
        "(largura 0,010); o tamanho indica quantos municípios há na faixa. Azuis entram na estimação (até 0,05 do "
        "corte, fundo cinza claro); cinzas ficam de fora. <b>Linhas azuis</b> = retas ajustadas separadamente de "
        "cada lado do corte. <b>Faixa azul clara</b> = incerteza da reta (IC 95%). <b>Traço preto no corte</b> = o "
        "degrau entre as duas retas, que é o efeito estimado; os percentuais ao lado são o valor de cada reta no "
        "corte. O degrau é pequeno diante da faixa de incerteza: não dá para distingui-lo de zero."),
    7: ("5. Separando a bolsa de outras políticas",
        "<b>Por quê:</b> outras regras federais mudam nos mesmos cortes, então medimos o degrau na <b>variação</b> "
        "da oferta (depois − antes do programa), o que cancela diferenças que já existiam. <b>Como ler:</b> cada "
        "bolinha é a média, numa faixa estreita de IVS, da variação de vínculos de especialistas no CNES por 10 mil "
        "habitantes; linhas e faixa azul como no gráfico anterior; o salto e seu IC estão no topo de cada painel. "
        "A faixa de incerteza cobre o zero nos dois cortes."),
}


def _figuras(html: str) -> list[str]:
    figs = re.findall(r'<figure class="fig">.*?</figure>', html, re.S)
    if len(figs) != len(EXPLICACOES):
        raise SystemExit(f"esperava {len(EXPLICACOES)} figuras no relatório de origem, achei {len(figs)}")
    novas = []
    for i in SELECIONADAS:
        fig = figs[i]
        titulo, texto = PASSOS.get(i, ("", EXPLICACOES[i]))
        fig = re.sub(r'<span class="fig-num">.*?</span>\s*', "", fig, count=1, flags=re.S)
        fig = re.sub(r'<div class="fig-sub">.*?</div>', "", fig, count=1, flags=re.S)
        fig = fig.replace("</figure>", f'<p class="explica">{texto}</p></figure>')
        cab = f'<h2>{titulo}</h2>' if titulo else ''
        novas.append(f'<section class="pagina">{cab}{fig}</section>')
    return novas


def _fmt(x: float, casas: int = 1) -> str:
    return f"{x:+.{casas}f}".replace(".", ",").replace("+-", "−").replace("-", "−")


def _linhas_resultado() -> list[dict]:
    """Linhas principais (h = 0,050), lidas de output/: E3 (RDD em nível) e E7 (DiRD no CNES, população U)."""
    import pandas as pd
    e3 = pd.read_csv(ROOT / "output" / "rdd_bolsa" / "E3_estimativas.csv")
    e3 = e3[(e3["especificacao"] == "principal") & (e3["h"] == 0.05)]
    nomes = {"fracao_celulas_ch1_com_confirmacao_ou_homologacao": "Vagas preenchidas na 1ª chamada (fração)",
             "D_k_especialista_ativo_do_ciclo": "Município com especialista ativo do ciclo"}
    linhas = []
    for _, r in e3.sort_values(["outcome", "ciclo_outcome", "corte"], ascending=[False, True, True]).iterrows():
        linhas.append(dict(resultado=nomes[r["outcome"]], ciclo=str(int(r["ciclo_outcome"])),
                           corte=f"{r['corte']:.3f}".replace(".", ","), n=f"{int(r['n_abaixo'])} / {int(r['n_acima'])}",
                           efeito=_fmt(100 * r["tau"]) + " p.p.",
                           ic=f"[{_fmt(100 * r['ic95_inf'])}; {_fmt(100 * r['ic95_sup'])}]",
                           p=f"{r['p_valor']:.2f}".replace(".", ","), zero=r["ic95_inf"] <= 0 <= r["ic95_sup"]))
    e7 = pd.read_csv(ROOT / "output" / "rdd_bolsa" / "E7_estimativas.csv")
    e7 = e7[(e7["outcome_id"] == "F3.1") & (e7["populacao"] == "U") & (e7["especificacao"] == "principal")]
    for _, r in e7.iterrows():
        corte = "empilhados" if r["corte"] == "empilhado" else f"{float(r['corte']):.3f}".replace(".", ",")
        linhas.append(dict(resultado="Especialistas no CNES, variação por 10 mil hab. (DiRD)", ciclo="1–2",
                           corte=corte, n=f"{int(r['n_abaixo'])} / {int(r['n_acima'])}", efeito=_fmt(r["tau"], 2),
                           ic=f"[{_fmt(r['ic95_inf'], 2)}; {_fmt(r['ic95_sup'], 2)}]",
                           p=f"{r['p_valor']:.2f}".replace(".", ","), zero=r["ic95_inf"] <= 0 <= r["ic95_sup"]))
    return linhas


def _pagina_resultado() -> str:
    linhas = _linhas_resultado()
    corpo = "".join(
        f"<tr><td class='txt'>{l['resultado']}</td><td>{l['ciclo']}</td><td>{l['corte']}</td><td>{l['n']}</td>"
        f"<td class='num'><b>{l['efeito']}</b></td><td class='num'>{l['ic']}</td><td class='num'>{l['p']}</td>"
        f"<td class='txt'>{'inclui zero' if l['zero'] else 'exclui zero'}</td></tr>" for l in linhas)
    todos_zero = all(l["zero"] for l in linhas)
    leitura = ("Todos os intervalos incluem zero: em nenhum resultado, corte ou ciclo o degrau é distinguível de zero."
               if todos_zero else "Ver a última coluna: há intervalo que exclui zero.")
    return ('<section class="pagina"><h2>3. Resultado: nenhum efeito detectável</h2>'
            '<table class="res"><thead><tr><th>Resultado</th><th>Ciclo</th><th>Corte</th>'
            '<th>Municípios abaixo / acima</th><th>Efeito (degrau)</th><th>IC 95%</th><th>p</th><th>IC</th></tr>'
            f'</thead><tbody>{corpo}</tbody></table>'
            '<p class="nota">Efeito = lado de bolsa maior − lado de bolsa menor, no corte. Regressão local linear, '
            'janela h = 0,050, kernel triangular, erro robusto. Fontes: <code>output/rdd_bolsa/E3_estimativas.csv</code> '
            'e <code>E7_estimativas.csv</code> (linhas principais).</p>'
            '<div class="cartoes">'
            f'<div class="cartao"><div class="rot">O que mostra</div>{leitura}</div>'
            '<div class="cartao"><div class="rot">Por que inconclusivo</div>Há poucas dezenas de municípios de cada '
            'lado do corte; os intervalos são largos e não descartam nem efeitos grandes, positivos ou negativos. '
            'Não é prova de efeito zero.</div>'
            '<div class="cartao"><div class="rot">Onde há mais precisão</div>A DiRD no CNES usa todos os municípios '
            'perto do corte, não só os com vaga; mesmo assim, sem degrau. Correção para testes múltiplos (Holm) não '
            'muda a leitura.</div></div></section>')


def montar_html() -> str:
    origem = ORIGEM.read_text(encoding="utf-8")
    estilo = re.search(r"<style>.*?</style>", origem, re.S).group(0)
    estilo = estilo.replace("</style>", (
        ".pagina { break-after: page; } .pagina:last-child { break-after: auto; }\n"
        "@page { size: A4 landscape; }\n main { max-width: 265mm; }\n"
        ".fig img, .fig svg { width: auto !important; max-width: 100%; max-height: 140mm; display: block; margin: 0 auto; }\n"
        ".explica { font-size: 11pt; line-height: 1.45; margin: 8pt 0 0; }\n"
        "h1 { font-size: 26pt; margin-top: 18mm; } .sub { color: var(--ink2); font-size: 12pt; margin: 0 0 10mm; }\n"
        ".pagina h2 { font-size: 16pt; border: 0; margin-bottom: 4pt; }\n"
        ".fig-titulo { font-size: 8.5pt; color: var(--ink2); font-weight: 400; }\n"
        ".cartoes { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5mm; }\n"
        ".cartao { background: var(--wash); border-radius: 6px; padding: 5mm; font-size: 11.5pt; line-height: 1.4; }\n"
        ".rot { font-size: 8.5pt; text-transform: uppercase; letter-spacing: .06em; color: var(--s1); font-weight: 650; margin-bottom: 2mm; }\n"
        "table.res { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 4mm 0 2mm; }\n"
        "table.res th, table.res td { padding: 2.2mm 2mm; border-bottom: 1px solid var(--grid); text-align: center; }\n"
        "table.res th { background: var(--wash); font-weight: 650; } table.res td.txt { text-align: left; }\n"
        ".nota { font-size: 8.5pt; color: var(--muted); margin-top: 8mm; }\n</style>"))
    capa = ('<section class="pagina"><h1>A bolsa maior atrai e fixa especialistas?</h1>'
            '<p class="sub">RDD do adicional de R$ 5 mil do PMM-E · visão geral para validação</p>'
            '<div class="cartoes">'
            '<div class="cartao"><div class="rot">Pergunta</div>O adicional de R$ 5 mil na bolsa, que depende do '
            'IVS do município, aumenta a presença de especialistas?</div>'
            '<div class="cartao"><div class="rot">Método</div>Regressão descontínua <i>sharp</i> com regressão '
            'linear local nos cortes de IVS 0,300 e 0,400; diferença em descontinuidades contra outras políticas nos '
            'mesmos cortes. Desenho padrão em economia.</div>'
            '<div class="cartao"><div class="rot">Resposta curta</div>Desenho válido. Nenhum efeito detectável sobre '
            'preenchimento, presença ou oferta; intervalos largos, portanto inconclusivo. Único sinal: candidatos '
            'preferem as vagas de bolsa maior.</div></div>'
            '<p class="nota">Detalhes, tabelas e diagnósticos: <code>relatorio_validacao_rdd_bolsa.pdf</code>. '
            'Salto = lado de bolsa maior − lado de bolsa menor. O contraste mede o incentivo marginal, não a '
            'participação no PMM-E.</p></section>')
    fim = ('<section class="pagina"><h2>6. O que concluímos</h2><div class="cartoes">'
           '<div class="cartao"><div class="rot">Validade</div>Regra exata nos cortes; sem manipulação do IVS.</div>'
           '<div class="cartao"><div class="rot">Efeito</div>Nenhum degrau detectável em preenchimento, presença ou '
           'oferta no CNES, em nenhum corte ou ciclo, mesmo após correção para testes múltiplos.</div>'
           '<div class="cartao"><div class="rot">Cautela</div>Poucas dezenas de municípios por lado: inconclusivo, '
           'não prova de efeito zero.</div>'
           '<div class="cartao"><div class="rot">Sinal</div>No ciclo 2, a bolsa muda <b>para onde</b> os candidatos '
           'querem ir, não <b>quantas</b> vagas são preenchidas.</div>'
           '<div class="cartao"><div class="rot">Próximo passo</div>Produção de consultas, exames e cirurgias por '
           'especialistas (SUS e planos) como medida mais próxima do objetivo da política.</div>'
           '</div></section>')
    figs = _figuras(origem)
    corpo = capa + figs[0] + figs[1] + _pagina_resultado() + figs[2] + figs[3] + fim
    return ('<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>RDD da bolsa: visão geral</title>{estilo}</head><body><main>{corpo}</main></body></html>\n')


def _imprimir_pdf(html_path: Path, pdf_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("rel09", ROOT / "scripts" / "rdd_bolsa" / "09_gerar_relatorio_pdf.py")
    rel09 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rel09)
    if not rel09.gerar_pdf(html_path, pdf_path):
        raise SystemExit("PDF não gerado")


def main() -> None:
    SAIDA_HTML.write_text(montar_html(), encoding="utf-8")
    _imprimir_pdf(SAIDA_HTML, SAIDA_PDF)
    print(f"gravado: {SAIDA_HTML.relative_to(ROOT)} e {SAIDA_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
