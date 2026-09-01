import numpy as np
import pandas as pd
from config import OUT_DIR

def calcular_diferencas(subgrupo):
    alvo = (subgrupo['uso_atual'] == 'Usa medicamento atualmente').astype(int)
    excluir = {'uso_atual', 'currently_medication', 'id_general', 'record_id', 'global_id', 'phq9_grupo'}
    colunas = [c for c in subgrupo.columns if c not in excluir]
    numericas = subgrupo[colunas].select_dtypes(include=[np.number, 'bool']).columns.tolist()
    resultados = []
    for coluna in numericas:
        usa = pd.to_numeric(subgrupo.loc[alvo == 1, coluna], errors='coerce').dropna()
        nao_usa = pd.to_numeric(subgrupo.loc[alvo == 0, coluna], errors='coerce').dropna()
        if len(usa) < 5 or len(nao_usa) < 5:
            continue
        variancia_pooled = (((len(usa)-1)*usa.var(ddof=1)) + ((len(nao_usa)-1)*nao_usa.var(ddof=1))) / (len(usa)+len(nao_usa)-2)
        dp_pooled = np.sqrt(variancia_pooled)
        smd = (usa.mean() - nao_usa.mean()) / dp_pooled if dp_pooled > 0 else np.nan
        resultados.append({'variavel': coluna, 'media_usa': usa.mean(), 'media_nao_usa': nao_usa.mean(), 'smd': smd, 'abs_smd': abs(smd), 'n_usa': len(usa), 'n_nao_usa': len(nao_usa)})
    tabela = pd.DataFrame(resultados).sort_values('abs_smd', ascending=False)
    tabela.to_csv(OUT_DIR / 'diferencas_descritivas_smd.csv', index=False)
    return tabela
