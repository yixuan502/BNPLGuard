"""Render the stage-three validation comparison for Markdown documentation."""
import json
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'outputs/.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

m=json.loads((ROOT/'outputs/metrics/validation_baselines.json').read_text())
fig,axes=plt.subplots(1,3,figsize=(10,3.5),layout='constrained')
colors=['#697887','#126b77']
for ax,(field,title,direction) in zip(axes,[('average_precision','Average precision','Higher is better'),('roc_auc','ROC-AUC','Higher is better'),('brier','Brier score','Lower is better')]):
    values=[m[k]['validation'][field] for k in ['dummy','logistic_regression']]
    bars=ax.bar(['Dummy','Logistic\nregression'],values,color=colors,width=.6)
    ax.bar_label(bars,labels=[f'{v:.4f}' for v in values],padding=4,fontsize=11)
    ax.set_ylim(0,1); ax.set_title(title+'\n'+direction,fontsize=11)
    ax.spines[['top','right']].set_visible(False); ax.grid(axis='y',alpha=.15); ax.set_axisbelow(True)
fig.suptitle('CFPB validation baselines | n = 1,270 | positive share = 38.66%',fontsize=13)
fig.supxlabel('Unweighted, one fixed split. No uncertainty intervals yet. Test set remains unevaluated.',fontsize=9)
fig.savefig(ROOT/'outputs/figures/validation_baselines.png',dpi=180)
