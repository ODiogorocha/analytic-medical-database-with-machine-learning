# Relatório da análise científica

## 1. Objetivo

Este relatório descreve a relação entre o escore PHQ-9, o uso atual autorreferido de medicamentos e as classes farmacológicas registradas na base. Também resume o modelo exploratório de aprendizado de máquina utilizado para discriminar uso atual e não uso atual.

## 2. Amostra analisada

A base contém **770 registros**. O escore PHQ-9 está disponível para **556 participantes**. Após aplicar o ponto de corte exploratório de PHQ-9 ≥ 10, foram identificados **338 participantes**.

No subconjunto com PHQ-9 ≥ 10, **97 participantes** declararam usar medicamento atualmente, **239** declararam não usar e **2** apresentaram informação ausente sobre uso atual.

## 3. Comparação descritiva

A tabela abaixo apresenta estatísticas do PHQ-9 segundo uso atual de medicamento.

| grupo                          |   Participantes |   Media |   Mediana |   Desvio_padrao |
|:-------------------------------|----------------:|--------:|----------:|----------------:|
| Não usa medicamento atualmente |             431 |   11.38 |        11 |            5.89 |
| Usa medicamento atualmente     |             123 |   14.61 |        15 |            5.65 |

## 4. Classes farmacológicas

As classes farmacológicas foram obtidas da tabela de medicamentos relacionada pelo identificador dos participantes. Quando uma pessoa possui mais de uma classe registrada, ela pode contribuir com mais de uma ocorrência. Portanto, as ocorrências não devem ser interpretadas como grupos mutuamente exclusivos.

Não há tabela de classes farmacológicas disponível.

## 5. Desempenho do modelo

| modelo                                  |   n |   n_features |   roc_auc_media |   roc_auc_dp |   f1_media |   acuracia_media |
|:----------------------------------------|----:|-------------:|----------------:|-------------:|-----------:|-----------------:|
| Random Forest exploratório do uso atual | 336 |          247 |           0.867 |        0.039 |      0.525 |            0.777 |

O modelo avalia **uso atual autorreferido de medicamento**, e não adesão correta ao tratamento.

## 6. Variáveis que diferenciam os grupos

As variáveis abaixo apresentam maiores diferenças padronizadas entre participantes que declararam usar e não usar medicamento no subconjunto com PHQ-9 ≥ 10.

| variavel                  |   media_usa |   media_nao_usa |    smd |   abs_smd |   n_usa |   n_nao_usa |
|:--------------------------|------------:|----------------:|-------:|----------:|--------:|------------:|
| mental_disorder_diagnosis |       1.113 |           1.766 | -1.738 |     1.738 |      97 |         239 |
| mental_disorders___1      |       0.732 |           0.163 |  1.389 |     1.389 |      97 |         239 |
| mental_disorders___2      |       0.567 |           0.117 |  1.072 |     1.072 |      97 |         239 |
| sedatives_score           |       1.639 |           0.522 |  0.647 |     0.647 |      72 |         178 |
| sedatives_1               |       1.708 |           0.804 |  0.638 |     0.638 |      72 |         179 |
| asrs_18                   |       1.968 |           1.317 |  0.581 |     0.581 |      62 |         126 |
| have_bad_dreams           |       1.853 |           1.303 |  0.531 |     0.531 |      68 |         175 |
| score_asrs18              |       0.629 |           0.373 |  0.526 |     0.526 |      62 |         126 |
| mental_disorders___8      |       0.206 |           0.042 |  0.513 |     0.513 |      97 |         239 |
| risco_sui_class           |       0.753 |           0.519 |  0.499 |     0.499 |      97 |         239 |
| more_drugs                |       0.328 |           0.126 |  0.495 |     0.495 |      64 |         175 |
| mental_disorders___3      |       0.155 |           0.021 |  0.484 |     0.484 |      97 |         239 |
| class_assist_sedatives    |       0.165 |           0.039 |  0.425 |     0.425 |      97 |         232 |
| mental_disorders___4      |       0.113 |           0.013 |  0.422 |     0.422 |      97 |         239 |
| mental_disorders___6      |       0.113 |           0.017 |  0.398 |     0.398 |      97 |         239 |

Essas diferenças são associações descritivas. Não demonstram causalidade, eficácia do medicamento ou adesão ao tratamento.

## 7. Limitações científicas

As bases não possuem uma variável específica de adesão, como doses esquecidas, proporção de doses tomadas, interrupção sem orientação, escala validada ou registro de dispensação. Assim, não é possível classificar cientificamente os participantes em “aderentes” e “não aderentes” com os dados atuais.

O PHQ-9 é utilizado como instrumento de rastreio e não confirma diagnóstico clínico. O estudo é observacional e transversal, e os resultados podem ser influenciados por dados faltantes, autorrelato, confundimento por indicação e codificação das variáveis. O modelo não deve ser utilizado isoladamente para decisões clínicas ou alteração de tratamentos.

## 8. Conclusão

A análise identificou 338 participantes com PHQ-9 ≥ 10, dos quais 97 declararam uso atual de medicamento e 239 declararam não uso. O pipeline de aprendizado de máquina e as visualizações podem apoiar a exploração científica da amostra, mas uma análise de adesão exigirá a inclusão de uma medida específica de comportamento medicamentoso.
