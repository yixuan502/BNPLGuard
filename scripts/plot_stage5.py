"""Render English evaluation figures from saved outputs without rescoring models."""
import argparse
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'outputs/.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LABELS={'logistic_regression':'LR (frozen selection)','dummy':'Dummy comparator','random_forest':'RF comparator'}
COLORS={'logistic_regression':'#126b77','dummy':'#697887','random_forest':'#7851a9'}

def render(directory):
    directory=Path(directory);directory=directory if directory.is_absolute() else ROOT/directory
    figs=directory/'figures';figs.mkdir(exist_ok=True)
    metrics=json.loads((directory/'test_metrics.json').read_text()); n=metrics['logistic_regression']['n'];prev=metrics['logistic_regression']['positive_rate']
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
    def save(fig,name):fig.savefig(figs/name,dpi=180,bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.7),layout='constrained')
    for name,m in metrics.items():
        roc=pd.read_csv(directory/f'{name}_roc.csv');pr=pd.read_csv(directory/f'{name}_pr.csv')
        axes[0].plot(roc.fpr,roc.tpr,color=COLORS[name],label=f'{LABELS[name]}: AUC {m["roc_auc"]:.3f}')
        axes[1].step(pr.recall,pr.precision,where='post',color=COLORS[name],label=f'{LABELS[name]}: AP {m["average_precision"]:.3f}')
    axes[0].plot([0,1],[0,1],color='black',ls=':',lw=1,label='Chance ranking')
    axes[1].axhline(prev,color='black',ls=':',lw=1,label=f'Positive share {prev:.3f}')
    for ax in axes:ax.set_xlim(0,1);ax.set_ylim(0,1.03);ax.legend(fontsize=8,loc='lower right');ax.grid(alpha=.15)
    axes[0].set(xlabel='False-positive rate',ylabel='True-positive rate',title='Test ROC curves')
    axes[1].set(xlabel='Recall',ylabel='Precision',title='Test precision-recall curves')
    fig.suptitle(f'Fixed models | test n = {n:,} | unweighted sample');save(fig,'test_roc_pr.png')
    fig,axes=plt.subplots(1,3,figsize=(11,3.7),layout='constrained')
    for ax,(name,m) in zip(axes,metrics.items()):
        matrix=np.array(m['confusion_matrix_tn_fp_fn_tp']).reshape(2,2).astype(int)
        ax.imshow(matrix,cmap='Blues',vmin=0,vmax=max(metrics['logistic_regression']['n']/2,1))
        for i in range(2):
            for j in range(2):ax.text(j,i,str(matrix[i,j]),ha='center',va='center',fontsize=14,color='white' if matrix[i,j]>n/3 else 'black')
        ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['No difficulty','Difficulty'],yticklabels=['No difficulty','Difficulty'],xlabel='Predicted label',ylabel='Actual label',title=LABELS[name])
        ax.tick_params(axis='x',labelsize=9)
    fig.suptitle('Test confusion matrices | threshold = 0.5 | respondent counts');save(fig,'test_confusion_matrices.png')
    cal=pd.read_csv(directory/'lr_calibration_bins.csv');pred=pd.read_csv(directory/'test_predictions.csv')
    nonempty=cal[cal.n>0]
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
    ax=axes[0];ax.plot([0,1],[0,1],ls=':',color='black',label='Ideal reference')
    ax.errorbar(nonempty.mean_prediction,nonempty.observed_rate,yerr=np.array([nonempty.observed_rate-nonempty.observed_wilson_lower,nonempty.observed_wilson_upper-nonempty.observed_rate]),fmt='o-',color=COLORS['logistic_regression'],capsize=3,label='Observed fraction with Wilson 95% interval')
    for _,r in nonempty.iterrows():ax.annotate(f'n={int(r.n)}',(r.mean_prediction,r.observed_rate),xytext=(0,10 if r.observed_rate<.9 else -16),textcoords='offset points',ha='center',fontsize=8)
    ax.set(xlim=(0,1),ylim=(-.03,1.07),xlabel='Mean LR predicted probability',ylabel='Observed difficulty fraction',title='LR reliability | 10 equal-width bins');ax.legend(fontsize=8,loc='lower right');ax.grid(alpha=.15)
    ax=axes[1];edges=np.arange(11)/10
    for label,color,text in [(0,'#697887','No difficulty'),(1,'#cb6b35','Difficulty')]:
        ax.hist(pred.loc[pred.y_true==label,'logistic_regression_probability'],bins=edges,histtype='step',lw=2,color=color,label=text)
    ax.axvline(.5,ls='--',color='black',lw=1,label='Fixed threshold 0.5')
    ax.set(xlim=(0,1),xlabel='Estimated probability of ENDSMEET = 2/3',ylabel='Respondents',title='LR test probability distribution');ax.legend(fontsize=8);ax.grid(axis='y',alpha=.15)
    fig.suptitle(f'Frozen LR probability diagnostics | test n = {n:,}')
    fig.supxlabel('Intervals are descriptive within-bin outcome uncertainty; small or empty bins limit interpretation.',fontsize=9);save(fig,'lr_test_reliability.png')
    imp=pd.read_csv(directory/'validation_permutation_importance.csv').sort_values('mean_ap_drop')
    fig,ax=plt.subplots(figsize=(8.5,4.8),layout='constrained')
    ax.barh(imp.feature,imp.mean_ap_drop,xerr=imp.sd_ap_drop,color=COLORS['logistic_regression'],capsize=3)
    ax.axvline(0,color='black',lw=1);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
    ax.set(xlabel='Validation AP drop after shuffling an original input column',title='Frozen LR global permutation importance')
    fig.supxlabel('30 permutations; error bars show SD across permutations, not a 95% CI. Associations are not causal.',fontsize=9);save(fig,'lr_validation_permutation.png')
    intervals=json.loads((directory/'bootstrap_intervals.json').read_text())['logistic_regression']
    fig,axes=plt.subplots(1,3,figsize=(9,3.5),layout='constrained')
    for ax,key,label in zip(axes,['average_precision','roc_auc','brier'],['Average precision','ROC-AUC','Brier score (lower is better)']):
        r=intervals[key];ax.errorbar([r['point']],[0],xerr=[[r['point']-r['lower']],[r['upper']-r['point']]],fmt='o',color=COLORS['logistic_regression'],capsize=6)
        ax.set(xlim=(0,1),ylim=(-1,1),yticks=[],xlabel=label,title=f"{r['point']:.3f} [{r['lower']:.3f}, {r['upper']:.3f}]")
        ax.grid(axis='x',alpha=.15)
    fig.suptitle('Frozen LR test metrics with paired-draw respondent bootstrap 95% intervals')
    fig.supxlabel('2,000 ordinary iid resamples; fixed-model uncertainty, not training or complex-survey uncertainty.',fontsize=9);save(fig,'lr_test_bootstrap_intervals.png')
    print(f'Saved five figure files to {figs}')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',default='outputs/evaluation/stage5_v1');args=parser.parse_args();render(args.output_dir)
