import numpy as np
import pandas as pd
from config import OUT_DIR

def preparar_grupos(relacionada):
    df = relacionada.copy()
    if 'phq9_score' not in df.columns:
        raise KeyError('A coluna phq9_score não foi encontrada.')
    if 'currently_medication' not in df.columns:
        raise KeyError('A coluna currently_medication não foi encontrada.')
    df['phq9_score'] = pd.to_numeric(df['phq9_score'], errors='coerce')
    df['uso_atual'] = df['currently_medication'].map({1: 'Usa medicamento atualmente', 2: 'Não usa medicamento atualmente'})
    df['phq9_grupo'] = np.select(
        [df['phq9_score'] < 10, df['phq9_score'] >= 10],
        ['PHQ-9 < 10', 'PHQ-9 ≥ 10'],
        default='PHQ-9 ausente'
    )
    subgrupo = df.loc[(df['phq9_score'] >= 10) & df['uso_atual'].notna()].copy()
    resumo = pd.DataFrame({
        'Indicador': ['Registros totais', 'PHQ-9 preenchido', 'PHQ-9 ≥ 10', 'Usa medicamento no PHQ-9 ≥ 10', 'Não usa medicamento no PHQ-9 ≥ 10', 'Uso ausente no PHQ-9 ≥ 10'],
        'Valor': [len(df), df['phq9_score'].notna().sum(), (df['phq9_score'] >= 10).sum(), ((df['phq9_score'] >= 10) & (df['uso_atual'] == 'Usa medicamento atualmente')).sum(), ((df['phq9_score'] >= 10) & (df['uso_atual'] == 'Não usa medicamento atualmente')).sum(), ((df['phq9_score'] >= 10) & df['uso_atual'].isna()).sum()]
    })
    comparacao = subgrupo.groupby('uso_atual')['phq9_score'].agg(Participantes='count', Media='mean', Mediana='median', Desvio_padrao='std').reset_index()
    resumo.to_csv(OUT_DIR / 'resumo_amostra.csv', index=False)
    comparacao.to_csv(OUT_DIR / 'comparacao_phq9_uso.csv', index=False)
    subgrupo.to_excel(OUT_DIR / 'subgrupo_phq9_maior_igual_10.xlsx', index=False)
    return df, subgrupo, resumo, comparacao
