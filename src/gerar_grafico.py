#!/usr/bin/env python3
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')
SCRIPT_DIR = Path(__file__).resolve().parent
BASE = SCRIPT_DIR.parent if SCRIPT_DIR.name == 'src' else SCRIPT_DIR
DATA = BASE / 'data'
if not DATA.exists():
    DATA = BASE
OUT = BASE / 'resultados_analise_medica' / 'graficos'
OUT.mkdir(parents=True, exist_ok=True)
F_BASE = DATA / 'Finalbaselinedatabase-Brazil-FederalUniversityofSantaMaria(withpostgraduatestudents).xlsx'
F_MED = DATA / 'Medicamentosdatabase-Brazil-FederalUniversityofSantaMaria.xlsx'

# Paleta e estilo constantes para manter consistência visual entre todas as figuras.
sns.set_theme(style='whitegrid', context='notebook')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':14,'axes.labelsize':11,'figure.dpi':150})
BLUE='#245b8f'; RED='#b23a48'; GREEN='#3a7d44'; GOLD='#c58b2a'; GRAY='#6b7280'

df = pd.read_excel(F_BASE)
dm = pd.read_excel(F_MED)
df.columns = [str(c).strip().lower() for c in df.columns]
dm.columns = [str(c).strip().lower() for c in dm.columns]
dm = dm.rename(columns={'global_id':'id_general'})
d = df.merge(dm, on='id_general', how='left', suffixes=('','_meddb'))
d['phq9'] = pd.to_numeric(d['phq9_score'], errors='coerce')
d['phq_grupo'] = pd.cut(d['phq9'], bins=[-0.1,4,9,14,19,27], labels=['Mínimo (0–4)','Leve (5–9)','Moderado (10–14)','Moderadamente grave (15–19)','Grave (20–27)'])
d['usa_medicamento'] = d['currently_medication'].map({1:'Usa atualmente',2:'Não usa atualmente'})

def save(name):
    plt.tight_layout(); plt.savefig(OUT/name, dpi=220, bbox_inches='tight'); plt.close()

# 1. Fluxo de inclusão da amostra.
fig, ax=plt.subplots(figsize=(8,4.8)); ax.axis('off')
steps=[('Base principal\n770 registros',0.85,BLUE),('PHQ-9 disponível\n556 registros',0.60,GREEN),('PHQ-9 ≥ 10\n338 registros',0.35,RED),('Subgrupo com uso atual\n97 usam | 239 não usam',0.10,GOLD)]
for i,(txt,y,c) in enumerate(steps):
    ax.text(.5,y,txt,ha='center',va='center',fontsize=14,fontweight='bold',color='white',bbox=dict(boxstyle='round,pad=.8',fc=c,ec='none'))
    if i<len(steps)-1: ax.annotate('',xy=(.5,y-.10),xytext=(.5,y-.035),arrowprops=dict(arrowstyle='-|>',lw=2,color=GRAY))
ax.set_title('Fluxo descritivo da amostra analisada',fontweight='bold'); save('01_fluxo_amostra.png')

# 2. Distribuição do PHQ-9.
plt.figure(figsize=(9,5)); sns.histplot(d['phq9'].dropna(), bins=range(0,29), discrete=True, color=BLUE, edgecolor='white'); plt.axvline(10,color=RED,ls='--',lw=2,label='Ponto de corte exploratório: 10'); plt.xlabel('Escore PHQ-9'); plt.ylabel('Número de participantes'); plt.title('Distribuição do escore PHQ-9'); plt.legend(); save('02_distribuicao_phq9.png')

# 3. Classes de severidade.
counts=d['phq_grupo'].value_counts().reindex(['Mínimo (0–4)','Leve (5–9)','Moderado (10–14)','Moderadamente grave (15–19)','Grave (20–27)']).fillna(0)
plt.figure(figsize=(9,5)); bars=plt.bar(counts.index,counts.values,color=[GREEN,BLUE,GOLD,RED,'#7f1d1d']); plt.ylabel('Número de participantes'); plt.title('Classificação descritiva do PHQ-9'); plt.xticks(rotation=18,ha='right');
for b,v in zip(bars,counts.values): plt.text(b.get_x()+b.get_width()/2,v+3,f'{int(v)}',ha='center',fontweight='bold')
save('03_classes_phq9.png')

# 4. Uso atual por classe de PHQ-9.
tab=pd.crosstab(d['phq_grupo'],d['usa_medicamento'],normalize='index').reindex(counts.index)
tab.plot(kind='bar',stacked=True,figsize=(9,5),color=[RED,BLUE]); plt.ylabel('Proporção dentro da classe'); plt.xlabel('Classe de PHQ-9'); plt.title('Uso atual de medicamento segundo a classe do PHQ-9'); plt.legend(title=''); plt.xticks(rotation=18,ha='right'); plt.ylim(0,1); save('04_uso_por_classe_phq9.png')

# 5. Boxplot PHQ por uso atual.
box=d.dropna(subset=['phq9','usa_medicamento']); plt.figure(figsize=(8,5)); sns.boxplot(data=box,x='usa_medicamento',y='phq9',hue='usa_medicamento',palette=[RED,BLUE],legend=False); sns.stripplot(data=box,x='usa_medicamento',y='phq9',color='black',alpha=.25,size=3); plt.xlabel(''); plt.ylabel('Escore PHQ-9'); plt.title('Escore PHQ-9 por uso atual autorreferido'); save('05_phq_por_uso_medicamento.png')

# 6. Classes farmacológicas no subgrupo PHQ>=10.
sub=d[(d.phq9>=10)&(d.usa_medicamento=='Usa atualmente')]
vals=[]
for c in ['rótulo da variável 1','rótulo da variável 2','rótulo da variável 3','rótulo da variável 4','rótulo da variável 5']:
    if c in sub: vals += sub[c].dropna().astype(str).tolist()
cls=pd.Series(vals).value_counts().sort_values()
plt.figure(figsize=(8,5)); plt.barh(cls.index,cls.values,color=BLUE); plt.xlabel('Ocorrências de classificação'); plt.title('Classes farmacológicas entre usuários com PHQ-9 ≥ 10');
for y,v in enumerate(cls.values): plt.text(v+.5,y,str(v),va='center')
save('06_classes_farmacologicas.png')

# 7. Dados faltantes das variáveis principais.
main=['phq9_score','currently_medication','which_medication','age','sex','bmi','gad7_score','psqi_score','score_suic']
miss=(100*d[main].isna().mean()).sort_values(ascending=True)
plt.figure(figsize=(8,5)); plt.barh(miss.index,miss.values,color=GOLD); plt.xlabel('Percentual ausente (%)'); plt.title('Dados faltantes em variáveis selecionadas');
for y,v in enumerate(miss.values): plt.text(v+.5,y,f'{v:.1f}%',va='center')
save('07_dados_faltantes.png')

# 8. Diferenças padronizadas, se o arquivo da análise corrigida existir.
eff=BASE/'resultados_analise_medica'/'diferencas_descritivas_smd.csv'
if eff.exists():
    e=pd.read_csv(eff).head(12).sort_values('smd'); plt.figure(figsize=(9,6)); colors=[RED if x<0 else BLUE for x in e.smd]; plt.barh(e.variavel,e.smd,color=colors); plt.axvline(0,color='black',lw=.8); plt.xlabel('Diferença padronizada: usa − não usa'); plt.title('Variáveis com maiores diferenças descritivas\nentre participantes com PHQ-9 ≥ 10'); save('08_diferencas_padronizadas.png')

# 9. Desempenho dos modelos, se houver métricas.
met=BASE/'resultados_analise_medica'/'metricas_modelo.csv'
if met.exists():
    m=pd.read_csv(met); metric_cols=[c for c in ['roc_auc_media','f1_media','acuracia_media'] if c in m]; long=m.melt(id_vars=['modelo'],value_vars=metric_cols,var_name='métrica',value_name='valor'); plt.figure(figsize=(8,5)); sns.barplot(data=long,x='métrica',y='valor',hue='modelo',palette='deep'); plt.ylim(0,1); plt.ylabel('Valor médio na validação cruzada'); plt.xlabel(''); plt.title('Desempenho do modelo exploratório'); plt.legend(title=''); save('09_desempenho_modelos.png')

# 10. Heatmap das escalas disponíveis para PHQ>=10.
corcols=['phq9_score','gad7_score','psqi_score','score_suic','score_psicose','score_asrs_final','scoretot_smile']
cor=d[d.phq9>=10][corcols].corr(min_periods=30); plt.figure(figsize=(8,6)); sns.heatmap(cor,annot=True,fmt='.2f',cmap='vlag',vmin=-1,vmax=1,square=True); plt.title('Correlação exploratória entre escores (PHQ-9 ≥ 10)'); save('10_heatmap_escores.png')

# Índice de figuras para facilitar uso no relatório.
index=['# Índice dos gráficos científicos\n','Os gráficos são descritivos e não demonstram causalidade. O campo `currently_medication` representa uso atual, não adesão correta.\n']
for p in sorted(OUT.glob('*.png')): index.append(f'- `{p.name}`\n')
(OUT/'README_graficos.md').write_text(''.join(index),encoding='utf-8')
print(f'Gerados {len(list(OUT.glob("*.png")))} gráficos em {OUT}')
