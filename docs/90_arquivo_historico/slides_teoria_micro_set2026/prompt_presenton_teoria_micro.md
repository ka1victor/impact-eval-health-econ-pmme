# Teoria Micro PMM-E — Prompt pronto para o Presenton

## Template escolhido: Executive
- **Onde:** https://presenton.ai/explore/executive
- **Por quê:** 32 layouts (o mais completo business), tipografia bold, estrutura crisp, acento violeta sutil.
  Ideal para equações e banca acadêmica (Insper). Sobriedade > criatividade aqui.
- **Preteridos:**
  - *Dynamic* (32 layouts, mas fundo escuro texturizado — ruim p/ equação e impressão)
  - *Momentum* (28, energético demais p/ teoria)
  - *General / Standard* (11–12 layouts, simples demais)
  - *Modern / Swift* (10/9, pitch de startup)

## Como fazer "lá" (2 min)
1. Acesse `presenton.ai/explore/executive` → **Use this template** (ou abra o app desktop: `presenton.ai/download`)
2. Escolha **Generate with AI → From prompt** (ou *From document* e anexe `docs/02_teoria/modelo_micro.md`)
3. Cole o PROMPT abaixo, 10 slides, idioma Português (BR)
4. Suba a figura `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` no slide 5
5. Exporte **PPTX editável** (e PDF p/ banca)

> Alternativa local/offline: `docker run -p 5000:80 ghcr.io/presenton/presenton:latest` → `http://localhost:5000`
> Deck espelho já gerado neste repo: `docs/02_teoria/slides_teoria_micro_presenton_executive.pptx`
> (mesma identidade Executive, 10 slides, editável — use como fallback ou como *custom template* via Upload PPTX)

---

## PROMPT (colar no Presenton)

```
Crie uma apresentação acadêmica de 10 slides em Português (BR), template Executive
(fundo claro, tipografia forte, acento violeta #6D28D9), título:
"Por que médicos escolhem onde atuar? Teoria Micro do PMM-E (Lei 15.233/2025)".

Público: banca de economia da saúde (Insper). Tom: rigoroso, conciso, equações em destaque.
Running variable canônica: IVS 2010 do IPEA. Não usar IDHM ou PIB per capita.

Slide 1 (capa escura): Por que médicos escolhem onde atuar? / Escolha locacional,
custo não-pecuniário e bolsa por IVS / Moehling et al.2020 + Choné&Ma 2011 + Reinhardt 1975.
Slide 2 (o puzzle): vagas de alto IVS ociosas; pergunta: que custo latente Δc0 a bolsa ΔB
(R$10k/15k/20k) precisa superar? Capital w=B+w(priv) vs interior w=B (subalocação).
Slide 3 (núcleo): Moehling et al.2020 eq.1 p.184:
argmax Σ δ^t [E[w]/p − c]. Explique i, δ, s, w, p, c. Adaptação PMM-E:
V = Σδ^t[E[w|B(IVS)]/p − c0(IVS)] + ε.
Slide 4 (geo): c_geo = φ(dist)−γA+θ; ∂c/∂dist>0, ∂c/∂A<0. Redding & Rossi-Hansberg eq.24.
Limite: CNES sem residência → município do estabelecimento.
Slide 5 (laboral, com figura curva em U): c(q)=C(q)−αB(q); C′>0 C′′>0; B′>0 B′′<0;
c′′≫0; q_cmax (C′=αB′), q_c=0 (C=αB). 3 zonas: crescente/decrescente/cansaço>satisfação.
Slide 6 (K,L): efeito duplo Reinhardt: ∂c/∂K<0, ∂c/∂L<0. Cirurgiões exigem K
(centro cirúrgico/UTI); clínicos toleram posto simples.
Slide 7 (integrada): equação-mestra c=[φ−γA+θ]+[C(q;L,K,s)−αB(q)]. 3 cards:
salário real / custo geo / custo clínico.
Slide 8 (IVS observável): c=c0(IVS). 3 subíndices IPEA: Infra (c↑), Capital Humano
(B′↑ mas K↓), Renda/Trabalho (w=B). Alerta: NÃO assumir c0′(IVS)>0 — forças opostas.
Slide 9 (hipóteses H1–H4): H1 compensação ΔB/p>Δc0; H2 subalocação interior<polo
(CNES 6/12m); H3 cirúrgico≪clínico em ∂Pr/∂IVS; H4 infra↓fixação, cap.hum.atenuado.
Slide 10 (takeaway escuro + refs): Bolsa compensa mas não resolve K,L,isolamento.
Refs: Moehling 2020; Choné&Ma 2011; Redding & Rossi-Hansberg 2017; Reinhardt 1975;
IPEA 2015; Costa-Nunes-Sanches 2024.
```

## Roteiro de fala (30s/slide)
1. Pergunta locacional. 2. Puzzle da vacância. 3. Moehling. 4. Geo. 5. Curva U.
6. K,L. 7. Equação-mestra. 8. IVS operacional. 9. H1–H4. 10. Takeaway.
