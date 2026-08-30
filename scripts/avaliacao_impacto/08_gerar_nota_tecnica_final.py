"""Gera nota técnica exclusivamente a partir dos artefatos da execução corrente."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_impacto"
REL = OUT / "relatorios"
MODELS = OUT / "modelos"


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def main() -> None:
    REL.mkdir(parents=True, exist_ok=True)
    gate = load(REL / "01_relatorio_portao_relevancia.json")
    sample = load(REL / "02_relatorio_painel_amostra.json")
    ddd = load(MODELS / "resultados_ddd_estatica.json")
    event = load(MODELS / "resultados_estudo_evento.json")
    mechanisms = load(MODELS / "resultados_mecanismos_fluxos.json")
    robustness = load(MODELS / "resultados_robustez_e_redistribuicao.json")

    primary = next(x for x in ddd if x["nome_modelo"] == "M1_DDD_Principal_Confirmatoria")
    expanded = next(x for x in ddd if x["nome_modelo"] == "M2_DDD_Ampliada")
    coverage = next(x for x in ddd if x["nome_modelo"] == "M3_DDD_Cobertura")
    pre = event["wald_pre_tendencias"]
    placebo = next(x for x in robustness["modelos"] if x["grupo_analise"] == "Placebo temporal")
    retention = mechanisms["presenca_6m_descritiva"]
    conditional_ok = gate["status_portao"] == "APROVADO" and pre["p_valor"] >= 0.10 and placebo["p_valor"] >= 0.10
    status = "INTERPRETAÇÃO CAUSAL CONDICIONAL" if conditional_ok else "COMPARAÇÃO AJUSTADA"
    first_stage = gate["resultados_ajustados"]["tem_alocado_muni_ddd"]
    gate_text = (
        "A modalidade imediata separou positivamente a alocação na amostra identificadora."
        if gate["status_portao"] == "APROVADO"
        else (
            "A modalidade imediata não separou a alocação na amostra identificadora; "
            "por isso, as regressões abaixo não identificam o impacto causal do programa."
        )
    )

    text = f"""# Nota técnica — vagas viram médicos e eles permanecem?

> Data da execução: {dt.date.today().isoformat()}
> Status: **{status}**
> Unidade principal: município–curso–mês
> Janela: 2024-06 a 2026-07

## Pergunta e estimando

A análise pergunta se disponibilizar inicialmente uma vaga do primeiro ciclo do
PMM-E para preenchimento imediato, em vez de mantê-la apenas em cadastro de
reserva, alterou o estoque cadastral de especialistas no município. O contraste
é uma intenção de tratar administrativa dentro do mesmo quadro de vagas; não
é PMM-E versus ausência do programa e não identifica individualmente bolsistas.

## Dados corrigidos

O painel usa exclusivamente os 26 arquivos mensais do CNES e todos os
estabelecimentos dos {sample['painel_municipal']['municipios']} municípios da
amostra. `CO_PROFISSIONAL_SUS` é deduplicado no município–curso–mês. A lista
nominal do PMM-E não é somada ao CNES, nenhuma carga horária é presumida e
competências ausentes interrompem o pipeline.

O universo confirmatório possui
{sample['painel_municipal']['celulas_confirmatorias']} células
município–curso. A especificação com variação dentro do município usa
{gate['amostra_ddd_municipio_curso']['n_celulas']} células em
{gate['amostra_ddd_municipio_curso']['n_municipios']} municípios com cursos nas
duas modalidades. Ela exclui cursos cujos CBOs são compartilhados com outro
curso do ciclo. A ponte é operacional e auditável, mas não é uma crosswalk
publicada pelo Ministério da Saúde.

## Relevância administrativa

O portão foi **{gate['status_portao']}** no mesmo grão e amostra da DDD. A
associação ajustada entre modalidade imediata e alocação confirmada foi
{100 * first_stage['beta']:.2f} p.p. (EP {100 * first_stage['se']:.2f};
p={first_stage['p_valor']:.4f}). {gate_text} A diferença observada no universo
CNES–curso não substitui esse teste no grão da análise. Homologação mede uma
candidatura homologada, não entrada em exercício no CNES.

## Resultado principal

A especificação DDD confirmatória, com efeitos fixos município–curso,
município–mês e curso–mês, produziu uma diferença ajustada de
**{fmt(primary['beta'])} especialista** por célula
(EP {fmt(primary['se'])}; IC 95% [{fmt(primary['ci_95'][0])},
{fmt(primary['ci_95'][1])}]; p={primary['p_valor']:.4f}). O intervalo deve ser
usado para avaliar tanto aumentos relevantes quanto reduções compatíveis com
os dados. Como o portão administrativo falhou na amostra identificadora, esse
número não deve ser chamado de efeito causal.

Na amostra ampliada dos 16 cursos, a estimativa foi {fmt(expanded['beta'])}
(IC 95% [{fmt(expanded['ci_95'][0])}, {fmt(expanded['ci_95'][1])}]). Para a
probabilidade de haver ao menos um especialista, a estimativa confirmatória foi
{100 * coverage['beta']:.2f} p.p. (IC 95% [{100 * coverage['ci_95'][0]:.2f},
{100 * coverage['ci_95'][1]:.2f}] p.p.).

## Dinâmica, entradas e presença posterior

Entradas exigem seis meses anteriores de ausência observada; saídas exigem três
meses posteriores consecutivos de ausência. As bordas sem seguimento são
censuradas, não preenchidas com zero.

Entre entrantes de 2025-08 a 2026-01, a presença no mesmo
município–curso seis meses depois foi
{retention['imediata']['taxa_presenca_6m_pct']:.1f}% na modalidade imediata e
{retention['reserva']['taxa_presenca_6m_pct']:.1f}% na reserva. Essa comparação
é descritiva porque condiciona em entrada, que pode ser afetada pelo tratamento.
A presença em doze meses permanece censurada até haver CNES até 2027-01.

## Diagnósticos de identificação

O teste conjunto dos coeficientes pré-tratamento produziu F={pre['estatistica_f']:.3f}
(p={pre['p_valor']:.4f}); o maior coeficiente pré em valor absoluto foi
{pre['max_abs_beta_pre']:.3f}. Não rejeitar a hipótese nula não prova tendências
paralelas. O placebo com falso início em 2025-01 estimou {fmt(placebo['beta'])}
(p={placebo['p_valor']:.4f}).

O painel regional é mantido apenas como diagnóstico descritivo. Como a exposição
é municipal e pode gerar interferência, ele não é apresentado como estimativa
causal de spillovers.

## Interpretação máxima

Esta execução não sustenta uma afirmação causal sobre o PMM-E. Ela mostra que,
na comparação ajustada escolhida, não apareceu aumento do estoque de
especialistas em municípios–cursos classificados como imediatos relativamente
aos mantidos em reserva. Isso não equivale a demonstrar que o programa não teve
efeito: o contraste perdeu relevância justamente na amostra que identifica a
DDD. O CNES mede presença cadastral total, não confirma que o profissional seja
bolsista, que cumpra horas efetivas, que produza procedimentos ou que melhore
desfechos de pacientes.

## Artefatos

- `tabelas/tabela1_estatisticas_descritivas_baseline.csv`
- `tabelas/tabela2_ddd_estatica_resultado_primario.csv`
- `tabelas/tabela3_mecanismos_fluxos_e_retencao.csv`
- `tabelas/tabela4_diagnosticos_robustez_e_redistribuicao.csv`
- `figuras/figura1_estudo_evento_ddd_dinamico.png`
- `figuras/figura2_diagnostico_redistribuicao.png`
- `figuras/figura3_trajetoria_estoque_por_modalidade.png`
- `figuras/figura4_decomposicao_mecanismos_fluxos.png`
"""
    target = REL / "03_nota_tecnica_avaliacao_impacto_pmme.md"
    target.write_text(text, encoding="utf-8")
    print(f"[OK] Nota técnica gerada com status: {status}")


if __name__ == "__main__":
    main()
