import pandas as pd
from config import localizar_planilha, BASE_NAMES, MED_NAMES, OUT_DIR

def limpar_colunas(df):
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def carregar_bases():
    arquivo_base = localizar_planilha(BASE_NAMES)
    arquivo_medicamentos = localizar_planilha(MED_NAMES)
    base = limpar_colunas(pd.read_excel(arquivo_base))
    medicamentos = limpar_colunas(pd.read_excel(arquivo_medicamentos))
    if 'global_id' in medicamentos.columns and 'id_general' not in medicamentos.columns:
        medicamentos = medicamentos.rename(columns={'global_id': 'id_general'})
    if 'id_general' not in base.columns or 'id_general' not in medicamentos.columns:
        raise KeyError('A chave id_general/global_id não foi encontrada nas duas bases.')
    relacionada = base.merge(medicamentos, on='id_general', how='left', suffixes=('', '_med'))
    relacionada.to_excel(OUT_DIR / 'base_relacionada.xlsx', index=False)
    print(f'Base principal: {arquivo_base}')
    print(f'Base de medicamentos: {arquivo_medicamentos}')
    print(f'Base relacionada: {relacionada.shape}')
    return base, medicamentos, relacionada
