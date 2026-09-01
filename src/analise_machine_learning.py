#!/usr/bin/env python3
from pathlib import Path
import re
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import make_scorer, f1_score

warnings.filterwarnings('ignore')
# Raiz do projeto: este arquivo deve estar em <projeto>/src/analise_medica.py.
# O fallback permite executar o script diretamente em outros diretórios.
SCRIPT_DIR = Path(__file__).resolve().parent
BASE = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'src' else SCRIPT_DIR
OUT = BASE / 'resultados_analise_medica'
OUT.mkdir(parents=True, exist_ok=True)
NOMES_BASE = [
    'Final baseline database - Brazil - Federal University of Santa Maria (with postgraduate students).xlsx',
    'Finalbaselinedatabase-Brazil-FederalUniversityofSantaMaria(withpostgraduatestudents).xlsx',
]
NOMES_MED = [
    'Medicamentos database - Brazil - Federal University of Santa Maria.xlsx',
    'Medicamentosdatabase-Brazil-FederalUniversityofSantaMaria.xlsx',
]

def normalizar_nome(nome):
    return ''.join(ch.lower() for ch in nome if ch.isalnum())

def localizar_arquivo(nomes):
    # Procura nomes exatos e, depois, compara nomes ignorando espaços, hífens e maiúsculas.
    candidatos = []
    for nome in nomes:
        candidatos.extend([BASE / 'data' / nome, BASE / nome])
    candidatos.extend(p for p in BASE.rglob('*.xlsx') if 'env' not in p.parts and '.git' not in p.parts)
    nomes_normalizados = {normalizar_nome(nome) for nome in nomes}
    for caminho in candidatos:
        if caminho.exists() and caminho.is_file() and normalizar_nome(caminho.name) in nomes_normalizados:
            return caminho
    locais = '\\n'.join(f'  - {BASE / "data" / nome}' for nome in nomes)
    raise FileNotFoundError(
        f'Planilha não encontrada. Coloque um destes nomes em data/:\\n{locais}'
    )

F_BASE = localizar_arquivo(NOMES_BASE)
F_MED = localizar_arquivo(NOMES_MED)
print(f'[INFO] Base principal: {F_BASE}')
print(f'[INFO] Base de medicamentos: {F_MED}')

# Carregamento e relacionamento: id_general (base principal) = global_id (medicamentos)
df = pd.read_excel(F_BASE)
dm = pd.read_excel(F_MED)
df.columns = [str(c).strip().lower() for c in df.columns]
dm.columns = [str(c).strip().lower() for c in dm.columns]
dm = dm.rename(columns={'global_id': 'id_general'})
merged = df.merge(dm, on='id_general', how='left', suffixes=('', '_meddb'), indicator=True)

# PHQ-9: usar o escore validado já calculado na base; não somar perguntas sem dicionário de codificação.
merged['phq9_score_final'] = pd.to_numeric(merged['phq9_score'], errors='coerce')
merged['phq9_positivo_10'] = np.where(merged['phq9_score_final'].notna(), (merged['phq9_score_final'] >= 10).astype(int), np.nan)
# Codificação observada na base: 1 = sim, 2 = não para currently_medication.
merged['medicacao_atual'] = merged['currently_medication'].map({1: 1, 2: 0})
merged['grupo_uso_atual'] = merged['medicacao_atual'].map({1: 'Usa medicamento atualmente', 0: 'Não usa medicamento atualmente'})

# Relatório de auditoria
lines = []
lines.append('# Auditoria e análise exploratória: PHQ-9 e medicamentos\n')
lines.append('## Conclusão metodológica central\n')
lines.append('As duas bases podem ser relacionadas por `id_general` na base principal e `global_id` na base de medicamentos. Entretanto, a planilha de medicamentos contém a classificação farmacológica, não uma medida de adesão (por exemplo: doses tomadas, esquecimento, escala de Morisky, retirada na farmácia ou registro eletrônico). Portanto, não é válido rotular alguém como “toma corretamente” ou “não toma corretamente” apenas com essas duas planilhas. A análise abaixo usa `currently_medication` somente como **uso atual autorreferido**, e não como adesão.\n')
lines.append('## Estrutura e relacionamento\n')
lines.append(f'- Base principal: {len(df)} registros e {df.shape[1]} variáveis.\n- Base de medicamentos: {len(dm)} registros e {dm.shape[1]} variáveis.\n- IDs únicos na base principal: {df.id_general.nunique()}; IDs únicos na base de medicamentos: {dm.id_general.nunique()}.\n- Registros relacionados após `left join`: {(merged._merge == "both").sum()}; sem correspondente na tabela de medicamentos: {(merged._merge == "left_only").sum()}.\n- PHQ-9 observado: {merged.phq9_score_final.notna().sum()} registros; PHQ-9 >= 10: {(merged.phq9_positivo_10 == 1).sum()}.\n')
lines.append('## Distribuição do uso atual entre participantes com PHQ-9 >= 10\n')
sub = merged[merged.phq9_positivo_10 == 1].copy()
tab = sub['grupo_uso_atual'].value_counts(dropna=False).rename_axis('grupo').reset_index(name='n')
tab['percentual'] = 100 * tab.n / tab.n.sum()
lines.append(tab.to_markdown(index=False) + '\n')
lines.append('## Comparação descritiva do escore PHQ-9 por uso atual\n')
comp = merged.dropna(subset=['phq9_score_final','medicacao_atual']).groupby('grupo_uso_atual')['phq9_score_final'].agg(['count','mean','median','std']).reset_index()
lines.append(comp.to_markdown(index=False) + '\n')
lines.append('## Variáveis disponíveis para uma análise exploratória\n')
lines.append('Foram selecionadas variáveis numéricas com pelo menos 50% de dados observados, excluindo identificadores, o próprio PHQ-9 e variáveis diretamente derivadas de `currently_medication`. O alvo exploratório é `medicacao_atual`; ele não representa adesão. A validação é estratificada e usa imputação dentro do pipeline.\n')

# features para alvo exploratório dentro de PHQ>=10
analysis = sub.dropna(subset=['medicacao_atual']).copy()
exclude = {'id_general','record_id','global_id','phq9_score','phq9_score_final','phq9_class','phq9_positivo_10','currently_medication','medicacao_atual'}
features = []
for c in analysis.columns:
    if c in exclude or c.endswith('_meddb') or analysis[c].dtype == 'object':
        continue
    if pd.api.types.is_numeric_dtype(analysis[c]) and analysis[c].notna().mean() >= 0.50 and analysis[c].nunique(dropna=True) > 1:
        features.append(c)
X = analysis[features].replace([np.inf,-np.inf], np.nan)
y = analysis['medicacao_atual'].astype(int)
summary = pd.DataFrame({'variavel': features, 'n_observado': [X[c].notna().sum() for c in features], 'n_unicos': [X[c].nunique(dropna=True) for c in features]})
summary.to_csv(OUT/'variaveis_modelo.csv', index=False)

# Associação descritiva: diferença padronizada entre grupos (não causal)
rows=[]
for c in features:
    a = X.loc[y==1,c].dropna(); b=X.loc[y==0,c].dropna()
    if len(a)>=5 and len(b)>=5:
        pooled=np.sqrt((a.var(ddof=1)+b.var(ddof=1))/2)
        smd=(a.mean()-b.mean())/pooled if pooled>0 else 0
        rows.append({'variavel':c,'media_usa':a.mean(),'media_nao_usa':b.mean(),'smd':smd,'abs_smd':abs(smd),'n_usa':len(a),'n_nao_usa':len(b)})
effect=pd.DataFrame(rows).sort_values('abs_smd',ascending=False)
effect.to_csv(OUT/'diferencas_descritivas_smd.csv', index=False)

if len(features) >= 2 and y.nunique()==2 and y.value_counts().min() >= 10:
    pipe=Pipeline([('imputer',SimpleImputer(strategy='median', add_indicator=True)),('rf',RandomForestClassifier(n_estimators=400,class_weight='balanced',random_state=42,n_jobs=-1,min_samples_leaf=3))])
    n_splits=min(5, int(y.value_counts().min()))
    cv=StratifiedKFold(n_splits=n_splits,shuffle=True,random_state=42)
    cvres=cross_validate(pipe,X,y,cv=cv,scoring={'roc_auc':'roc_auc','f1':'f1','accuracy':'accuracy'})
    metrics=pd.DataFrame([{'modelo':'Random Forest exploratório do uso atual','n':len(y),'n_features':len(features),'roc_auc_media':cvres['test_roc_auc'].mean(),'roc_auc_dp':cvres['test_roc_auc'].std(),'f1_media':cvres['test_f1'].mean(),'acuracia_media':cvres['test_accuracy'].mean()}])
    metrics.to_csv(OUT/'metricas_modelo.csv',index=False)
    pipe.fit(X,y)
    perm=permutation_importance(pipe,X,y,n_repeats=20,random_state=42,scoring='roc_auc',n_jobs=-1)
    imp=pd.DataFrame({'variavel':features,'importancia_permutacao_media':perm.importances_mean,'importancia_permutacao_dp':perm.importances_std}).sort_values('importancia_permutacao_media',ascending=False)
    imp.to_csv(OUT/'importancia_permutacao.csv',index=False)
    top=imp.head(15).sort_values('importancia_permutacao_media')
    plt.figure(figsize=(9,6)); plt.barh(top.variavel,top.importancia_permutacao_media,color='#245b8f'); plt.xlabel('Queda média do ROC-AUC ao permutar'); plt.title('Variáveis mais informativas para uso atual\n(não é adesão medicamentosa)'); plt.tight_layout(); plt.savefig(OUT/'importancia_variaveis.png',dpi=220); plt.close()
    lines.append('## Modelo exploratório do uso atual entre PHQ-9 >= 10\n')
    lines.append(metrics.to_markdown(index=False) + '\n')
    lines.append('As variáveis abaixo são apenas informativas para discriminar o uso atual nesta amostra; não devem ser interpretadas como causas nem como fatores comprovados de adesão.\n')
    lines.append(imp.head(15).to_markdown(index=False) + '\n')
else:
    lines.append('Não foi possível executar validação cruzada confiável: faltam variáveis ou há poucos casos em uma classe.\n')

lines.append('## O que falta para medir adesão corretamente\n')
lines.append('É necessário um campo de adesão observado ou autorreferido, com definição anterior à análise. Exemplos: proporção de doses tomadas no período, número de doses esquecidas, interrupção sem orientação, escala validada ou dados de dispensação. Com esse campo, o alvo deverá ser criado com regras documentadas e a análise deverá excluir o próprio indicador de adesão das preditoras para evitar vazamento de informação.\n')
lines.append('## Limitações\n')
lines.append('O desenho é observacional e transversal; associação não implica causalidade. O PHQ-9 é um instrumento de rastreio e não confirma diagnóstico. Dados faltantes, autorrelato, codificação numérica sem dicionário e possível confundimento por indicação podem alterar os resultados. Modelos treinados nesta amostra não devem ser usados para decidir tratamento de pessoas.\n')
(OUT/'relatorio_analise.md').write_text('\n'.join(lines), encoding='utf-8')
merged.to_excel(OUT/'base_relacionada_phq9_medicamentos.xlsx', index=False)
print('OK', OUT)
print('shape merged', merged.shape, 'PHQ>=10', len(sub), 'features', len(features))
print(tab.to_string(index=False))
