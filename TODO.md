# TODO.md — Fila de Pesquisa e Próximos Passos do PMM-E

---

## 🟢 Etapas Concluídas e Validadas

- [x] Extração e compilação de 1.480 médicos ativos no PMM-E (`data/pmm_especialistas_nominal.csv`);
- [x] Compilação universal do IVS 2010 para os 5.565 municípios brasileiros (`data/ivs_ipea_2010_municipios.csv`);
- [x] Estimação de primeiro estágio de RDD e elasticidade-salário de oferta médica ($\varepsilon_1 = 1{,}48$ e $\varepsilon_2 = 0{,}31$);
- [x] Testes de densidade e placebos em cortes falsos ($IVS = 0{,}250$ e $0{,}350$);
- [x] Decomposição de resolutividade local vs. global com 3,77M linhas do SIA e 1,35M do SIH;
- [x] Análise de custo-benefício estrita (BCR logístico de 2,4x) e ampliada (95,4x);
- [x] Teste de validação do gradiente de distância com teleconsulta ($\beta = -0{,}11$ vs $-1{,}40$).

---

## 🟡 Próximos Passos e Fila de Expansão

- [ ] Incorporação de novas competências mensais do SIA e SIH (2º semestre de 2026);
- [ ] Análise de heterogeneidade por macrorregião (Nordeste vs. Norte vs. Centro-Oeste);
- [ ] Estimação do tempo de espera contrafactual no SUS para cirurgias eletivas nas cidades tratadas;
- [ ] Elaboração do rascunho do paper acadêmico (Introduction, Institutional Background, Empirical Strategy, Results, Policy Implications).
