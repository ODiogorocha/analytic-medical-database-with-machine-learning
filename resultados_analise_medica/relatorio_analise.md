# Auditoria e análise exploratória: PHQ-9 e medicamentos

## Conclusão metodológica central

As duas bases podem ser relacionadas por `id_general` na base principal e `global_id` na base de medicamentos. Entretanto, a planilha de medicamentos contém a classificação farmacológica, não uma medida de adesão (por exemplo: doses tomadas, esquecimento, escala de Morisky, retirada na farmácia ou registro eletrônico). Portanto, não é válido rotular alguém como “toma corretamente” ou “não toma corretamente” apenas com essas duas planilhas. A análise abaixo usa `currently_medication` somente como **uso atual autorreferido**, e não como adesão.

## Estrutura e relacionamento

- Base principal: 770 registros e 291 variáveis.
- Base de medicamentos: 769 registros e 12 variáveis.
- IDs únicos na base principal: 770; IDs únicos na base de medicamentos: 769.
- Registros relacionados após `left join`: 769; sem correspondente na tabela de medicamentos: 1.
- PHQ-9 observado: 556 registros; PHQ-9 >= 10: 338.

## Distribuição do uso atual entre participantes com PHQ-9 >= 10

| grupo                          |   n |   percentual |
|:-------------------------------|----:|-------------:|
| Não usa medicamento atualmente | 239 |    70.7101   |
| Usa medicamento atualmente     |  97 |    28.6982   |
| nan                            |   2 |     0.591716 |

## Comparação descritiva do escore PHQ-9 por uso atual

| grupo_uso_atual                |   count |    mean |   median |     std |
|:-------------------------------|--------:|--------:|---------:|--------:|
| Não usa medicamento atualmente |     431 | 11.3759 |       11 | 5.89188 |
| Usa medicamento atualmente     |     123 | 14.6098 |       15 | 5.64617 |

## Variáveis disponíveis para uma análise exploratória

Foram selecionadas variáveis numéricas com pelo menos 50% de dados observados, excluindo identificadores, o próprio PHQ-9 e variáveis diretamente derivadas de `currently_medication`. O alvo exploratório é `medicacao_atual`; ele não representa adesão. A validação é estratificada e usa imputação dentro do pipeline.

## Modelo exploratório do uso atual entre PHQ-9 >= 10

| modelo                                  |   n |   n_features |   roc_auc_media |   roc_auc_dp |   f1_media |   acuracia_media |
|:----------------------------------------|----:|-------------:|----------------:|-------------:|-----------:|-----------------:|
| Random Forest exploratório do uso atual | 336 |          247 |        0.866577 |    0.0386009 |   0.525106 |         0.777041 |

As variáveis abaixo são apenas informativas para discriminar o uso atual nesta amostra; não devem ser interpretadas como causas nem como fatores comprovados de adesão.

| variavel         |   importancia_permutacao_media |   importancia_permutacao_dp |
|:-----------------|-------------------------------:|----------------------------:|
| psycotherapy     |                    8.41134e-05 |                 8.23812e-05 |
| to_sleep         |                    7.33296e-05 |                 2.40166e-05 |
| score_asrs18     |                    4.74486e-05 |                 2.32289e-05 |
| smile_25         |                    4.52918e-05 |                 2.14594e-05 |
| gad7_score       |                    4.31351e-05 |                 0           |
| scoretot_smile   |                    4.09783e-05 |                 9.40107e-06 |
| ver_phq          |                    4.09783e-05 |                 9.40107e-06 |
| touch_obj        |                    4.09783e-05 |                 9.40107e-06 |
| score_asrs_final |                    4.09783e-05 |                 9.40107e-06 |
| hcl_16_score     |                    4.09783e-05 |                 9.40107e-06 |
| height           |                    4.09783e-05 |                 9.40107e-06 |
| income           |                    3.88216e-05 |                 1.29405e-05 |
| treatment        |                    3.88216e-05 |                 1.29405e-05 |
| moving_slowly    |                    3.88216e-05 |                 1.29405e-05 |
| alcohol_2        |                    3.88216e-05 |                 1.29405e-05 |

## O que falta para medir adesão corretamente

É necessário um campo de adesão observado ou autorreferido, com definição anterior à análise. Exemplos: proporção de doses tomadas no período, número de doses esquecidas, interrupção sem orientação, escala validada ou dados de dispensação. Com esse campo, o alvo deverá ser criado com regras documentadas e a análise deverá excluir o próprio indicador de adesão das preditoras para evitar vazamento de informação.

## Limitações

O desenho é observacional e transversal; associação não implica causalidade. O PHQ-9 é um instrumento de rastreio e não confirma diagnóstico. Dados faltantes, autorrelato, codificação numérica sem dicionário e possível confundimento por indicação podem alterar os resultados. Modelos treinados nesta amostra não devem ser usados para decidir tratamento de pessoas.
