# CLAUDE.md — Diretrizes Metodológicas e Regras de Desenvolvimento

> Repositório dedicado à avaliação de impacto causal e economia da saúde do **Programa Mais Médicos Especialistas (PMM-E)**.

---

## 1. As Cinco Regras Metodológicas

1. **Rigor Causal Primeiro:** Toda afirmação de efeito causal deve ser sustentada pelo RDD no corte institucional do IVS 2010 ($IVS = 0{,}300$ ou $0{,}400$).
2. **Inferência Exata:** Reportar sempre erro-padrão robusto clusterizado, estatística $t$ e $p$-valor de permutação exata (mínimo de 2.000 repetições).
3. **Controle de Testes Múltiplos:** Em famílias de múltiplos desfechos, aplicar FDR de Anderson / Benjamini-Hochberg e Índice Padronizado de Kling-Liebman-Katz (2007).
4. **Validação de Placebos:** Qualquer resultado só é promovido se os testes de falsos cortes ($IVS = 0{,}250$ e $0{,}350$) resultarem em efeitos estritamente nulos ($p > 0{,}10$).
5. **Proveniência Obrigatória dos Dados:**
   - ✅ **Auditado e Verificado:** Microdados oficiais do Ministério da Saúde (SIA, SIH, CNES, SGTES) e IPEA;
   - ⚠️ **Parâmetro / Premissa:** Valores médios operacionais de transporte ou conversão de QALYs;
   - ❓ **Dado Não Observável / Hipótese Não Testável.**

---

## 2. Padrão de Motivação de Política Pública

Todo documento ou seção de motivação deve conter as 4 propriedades obrigatórias do projeto:
1. **Nomeia quem usa o número e para quê;**
2. **Converte o achado em decisão, não em adjetivo;**
3. **Tem uma predição com direção e data;**
4. **Declara o limite do que o número sustenta.**
