import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from config import OUT_DIR

def executar_modelo(subgrupo, medicamentos):
    y = (subgrupo['uso_atual'] == 'Usa medicamento atualmente').astype(int)
    excluir = {'uso_atual', 'currently_medication', 'id_general', 'record_id', 'global_id', 'phq9_grupo'}
    colunas_med = set(medicamentos.columns) - {'id_general'}
    colunas = [c for c in subgrupo.columns if c not in excluir and c not in colunas_med]
    X = subgrupo[colunas].copy()
    for c in X.columns:
        if pd.api.types.is_datetime64_any_dtype(X[c]):
            X[c] = X[c].astype(str)
    numericas = X.select_dtypes(include=[np.number, 'bool']).columns.tolist()
    categoricas = [c for c in X.columns if c not in numericas]
    transformador = ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), numericas),
        ('cat', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))]), categoricas)
    ])
    modelo = Pipeline([
        ('preprocessamento', transformador),
        ('classificador', RandomForestClassifier(n_estimators=400, class_weight='balanced', min_samples_leaf=2, random_state=42, n_jobs=-1))
    ])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    resultado = cross_validate(modelo, X, y, cv=cv, scoring={'roc_auc':'roc_auc', 'f1':'f1', 'accuracy':'accuracy'})
    metricas = pd.DataFrame([{
        'modelo': 'Random Forest exploratório do uso atual', 'n': len(X), 'n_features_originais': len(colunas),
        'roc_auc_media': resultado['test_roc_auc'].mean(), 'roc_auc_dp': resultado['test_roc_auc'].std(),
        'f1_media': resultado['test_f1'].mean(), 'acuracia_media': resultado['test_accuracy'].mean()
    }])
    metricas.to_csv(OUT_DIR / 'metricas_modelo.csv', index=False)
    modelo.fit(X, y)
    try:
        nomes = modelo.named_steps['preprocessamento'].get_feature_names_out()
        imp = pd.DataFrame({'variavel': nomes, 'importancia': modelo.named_steps['classificador'].feature_importances_}).sort_values('importancia', ascending=False)
        imp.head(30).to_csv(OUT_DIR / 'importancia_variaveis_modelo.csv', index=False)
    except Exception:
        pass
    return modelo, metricas
