import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import GRAF_DIR

NAVY, BLUE, TEAL, GOLD, CORAL, MUTED = '#173F5F', '#20639B', '#3CAEA3', '#F6C85F', '#ED553B', '#64748B'

def _salvar(fig, nome, titulo, subtitulo):
    fig.suptitle(titulo, x=.06, y=.98, ha='left', color=NAVY, fontsize=18, fontweight='bold')
    fig.text(.06, .945, subtitulo, ha='left', va='top', fontsize=10, color=MUTED)
    fig.text(.06, .015, 'Fonte: base UFSM | análise exploratória | uso atual não equivale a adesão', fontsize=8, color=MUTED)
    fig.tight_layout(rect=[0, .04, 1, .92])
    fig.savefig(GRAF_DIR / nome, dpi=220, bbox_inches='tight')
    plt.close(fig)

def gerar_graficos(df, subgrupo, metricas, efeitos):
    sns.set_theme(style='whitegrid', context='notebook')
    plt.rcParams.update({'font.family':'DejaVu Sans', 'axes.titlesize':16, 'axes.titleweight':'bold'})
    # 1. Distribuição PHQ-9.
    fig, ax = plt.subplots(figsize=(10, 5.5)); vals = df['phq9_score'].dropna()
    ax.hist(vals, bins=np.arange(-.5, 28.5, 1), color=BLUE, edgecolor='white'); ax.axvspan(9.5, 28, color=CORAL, alpha=.1); ax.axvline(9.5, color=CORAL, ls='--', lw=2); ax.text(10, .93, 'PHQ-9 ≥ 10', transform=ax.get_xaxis_transform(), color=CORAL, fontweight='bold'); ax.set(xlabel='Escore PHQ-9', ylabel='Participantes'); sns.despine(ax=ax); _salvar(fig, '01_distribuicao_phq9.png', 'Distribuição dos escores PHQ-9', 'A área colorida destaca o ponto de corte exploratório.')
    # 2. Grupos.
    grupos = subgrupo['uso_atual'].value_counts().reindex(['Não usa medicamento atualmente','Usa medicamento atualmente']).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 5.5)); bars=ax.bar(grupos.index, grupos.values, color=[CORAL, BLUE], width=.58)
    for b,v in zip(bars,grupos.values): ax.text(b.get_x()+b.get_width()/2, v+max(grupos)*.025, f'{int(v)}\n{v/grupos.sum()*100:.1f}%', ha='center', fontweight='bold')
    ax.set_ylim(0,max(grupos)*1.2); ax.set_ylabel('Participantes'); ax.tick_params(axis='x',rotation=10); sns.despine(ax=ax); _salvar(fig, '02_grupos_uso_atual.png', 'Como os participantes foram separados', 'Somente pessoas com PHQ-9 ≥ 10 e resposta válida sobre uso atual entram nesta comparação.')
    # 3. PHQ-9 por grupo.
    fig, ax = plt.subplots(figsize=(8,5.5)); palette={'Não usa medicamento atualmente':CORAL,'Usa medicamento atualmente':BLUE}; sns.violinplot(data=subgrupo,x='uso_atual',y='phq9_score',hue='uso_atual',palette=palette,inner=None,cut=0,legend=False,ax=ax,alpha=.4); sns.boxplot(data=subgrupo,x='uso_atual',y='phq9_score',hue='uso_atual',palette=palette,width=.22,showfliers=False,legend=False,ax=ax); ax.set(xlabel='',ylabel='Escore PHQ-9'); ax.tick_params(axis='x',rotation=10); sns.despine(ax=ax); _salvar(fig, '03_phq9_por_uso.png', 'PHQ-9 segundo o uso atual de medicamento', 'A caixa mostra a mediana e a distribuição de cada grupo.')
    # 4. Ausentes.
    miss=(df.isna().mean()*100).sort_values().tail(15); fig,ax=plt.subplots(figsize=(9,6)); bars=ax.barh(miss.index,miss.values,color=GOLD)
    for b,v in zip(bars,miss.values): ax.text(v+1,b.get_y()+b.get_height()/2,f'{v:.1f}%',va='center',fontsize=9)
    ax.set_xlabel('Percentual ausente'); ax.set_xlim(0,max(miss.max()*1.18,5)); sns.despine(ax=ax); _salvar(fig, '04_dados_ausentes.png', 'Qualidade dos dados: valores ausentes', 'Variáveis com maior ausência podem reduzir a precisão das comparações.')
    # 5. SMD.
    if not efeitos.empty:
        top=efeitos.head(12).sort_values('smd'); fig,ax=plt.subplots(figsize=(9,6)); ax.barh(top['variavel'],top['smd'],color=[CORAL if v<0 else BLUE for v in top['smd']]); ax.axvline(0,color='#1F2937'); ax.set_xlabel('Diferença padronizada (usa − não usa)'); sns.despine(ax=ax); _salvar(fig, '05_diferencas_padronizadas.png', 'Variáveis que mais diferenciam os grupos', 'Valores maiores em módulo indicam diferença descritiva, não causa.')
    # 6. Métricas.
    met=metricas.iloc[0]; labels=['ROC-AUC','F1-score','Acurácia']; values=[met.roc_auc_media,met.f1_media,met.acuracia_media]; fig,ax=plt.subplots(figsize=(8,5.5)); bars=ax.bar(labels,values,color=[BLUE,CORAL,TEAL],width=.58)
    for b,v in zip(bars,values): ax.text(b.get_x()+b.get_width()/2,v+.025,f'{v:.3f}',ha='center',fontweight='bold')
    ax.set_ylim(0,1); ax.set_ylabel('Média na validação cruzada'); sns.despine(ax=ax); _salvar(fig, '06_desempenho_modelo.png', 'Desempenho do modelo exploratório', 'O alvo é uso atual de medicamento, não adesão.')
