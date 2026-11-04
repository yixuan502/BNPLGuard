"""Independent recorded-label experiment. Never reads CFPB data or artifacts."""
import argparse
import itertools
import json
import os
import warnings
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .common import ROOT, read_json, write_json, sha256
from .evaluation_stats import binary_metrics, paired_bootstrap, calibration_bins

NAMES=['dummy','logistic_regression','random_forest']
DEFAULT_RUN='models/kaggle/exploratory_v1'
DEFAULT_OUT='outputs/kaggle_experiment/v1'


def load_data():
    cfg=read_json('config/kaggle_experiment.json');schema=read_json('config/kaggle_feature_schema.json')
    if sha256(ROOT/cfg['data'])!=cfg['data_sha256'] or sha256(ROOT/'config/kaggle_feature_schema.json')!=cfg['schema_sha256']:
        raise ValueError('Sealed source or schema changed')
    raw=pd.read_csv(ROOT/cfg['data']);frame=raw.copy(deep=True)
    target=pd.to_numeric(frame.default_flag,errors='coerce')
    if (frame.default_flag.notna()&~target.isin([0,1])).any():raise ValueError('Unparseable or nonbinary label; never coerce to negative')
    frame=frame.loc[target.notna()].copy();frame['default_flag']=target.loc[frame.index].astype(int)
    if frame.user_id.isna().any() or frame.user_id.duplicated().any():raise ValueError('Unique nonmissing user IDs required; grouped design needed otherwise')
    if frame.duplicated().any():raise ValueError('Unexpected duplicates need a reviewed protocol, not silent deletion')
    for name in schema['numeric']:
        parsed=pd.to_numeric(frame[name],errors='coerce')
        if (frame[name].notna()&parsed.isna()).any() or np.isinf(parsed).any():raise ValueError(f'Invalid numeric field: {name}')
        frame[name]=parsed
    flow=[{'step':'raw','n':len(raw)},{'step':'missing label excluded, never imputed','excluded_n':int(target.isna().sum()),'n':len(frame)},
          {'step':'no outlier removal, clipping, duplicate deletion or financial-unit conversion','n':len(frame)}]
    return cfg,schema,frame.set_index('user_id',drop=False),flow


def get_split(frame,cfg):
    path=ROOT/cfg['split_file']
    if not path.exists():
        dev,test=train_test_split(frame.index.to_numpy(),test_size=.2,stratify=frame.default_flag,random_state=cfg['seed'])
        train,val=train_test_split(dev,test_size=.25,stratify=frame.loc[dev,'default_flag'],random_state=cfg['seed'])
        write_json(path,{'data_sha256':cfg['data_sha256'],'seed':cfg['seed'],'semantic_grain':'One recorded row per ID; real person/transaction identity unconfirmed',
                         'train':[int(x) for x in train],'validation':[int(x) for x in val],'test':[int(x) for x in test]})
    split=read_json(path);sets=[set(split[k]) for k in ['train','validation','test']]
    assert split['data_sha256']==cfg['data_sha256'] and split['seed']==cfg['seed']
    assert all(not sets[i]&sets[j] for i in range(3) for j in range(i+1,3))
    assert set.union(*sets)==set(frame.index)
    assert all(len(split[k])==len(set(split[k])) for k in ['train','validation','test'])
    return split


def build_pipeline(estimator,schema):
    num=Pipeline([('imputer',SimpleImputer(strategy='median',keep_empty_features=True)),('scaler',StandardScaler())])
    cat=Pipeline([('imputer',SimpleImputer(strategy='most_frequent',keep_empty_features=True)),('onehot',OneHotEncoder(handle_unknown='ignore'))])
    return Pipeline([('preprocessor',ColumnTransformer([('numeric',num,schema['numeric']),('categorical',cat,schema['categorical'])],remainder='drop')),
                     ('classifier',estimator)])


def estimators(cfg):
    yield 'dummy',{},DummyClassifier(strategy='prior')
    for c in cfg['lr_C']:yield 'logistic_regression',{'C':c},LogisticRegression(C=c,max_iter=2000,solver='lbfgs',random_state=cfg['seed'])
    g=cfg['rf_grid']
    for n,depth,leaf in itertools.product(g['n_estimators'],g['max_depth'],g['min_samples_leaf']):
        params={'n_estimators':n,'max_depth':depth,'min_samples_leaf':leaf}
        yield 'random_forest',params,RandomForestClassifier(**params,max_features='sqrt',n_jobs=1,random_state=cfg['seed'])


def train(run_dir=DEFAULT_RUN,output_dir=DEFAULT_OUT):
    cfg,schema,frame,flow=load_data();split=get_split(frame,cfg);run=ROOT/run_dir;out=ROOT/output_dir
    if run.exists() or out.exists():raise FileExistsError('Preserve prior run; use new --run-dir and --output-dir')
    run.mkdir(parents=True);out.mkdir(parents=True)
    write_json(out/'protocol_before_training.json',cfg);write_json(out/'feature_schema.json',schema);write_json(out/'sample_flow.json',flow)
    write_json(out/'split_accounting.json',{k:{'n':len(split[k]),'positive_n':int(frame.loc[split[k],'default_flag'].sum())} for k in ['train','validation','test']})
    tr=frame.loc[split['train']];va=frame.loc[split['validation']]
    xt=tr[schema['features']];xv=va[schema['features']];yt=tr.default_flag;yv=va.default_flag
    cv=StratifiedKFold(n_splits=cfg['cv_folds'],shuffle=True,random_state=cfg['seed']);rows=[];candidates=[]
    for i,(name,params,estimator) in enumerate(estimators(cfg)):
        pipe=build_pipeline(estimator,schema)
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always')
            scores=cross_validate(pipe,xt,yt,cv=cv,scoring={'ap':'average_precision','auc':'roc_auc','brier':'neg_brier_score'},return_train_score=True,error_score='raise',n_jobs=1)
        if any(issubclass(w.category,ConvergenceWarning) for w in ws):raise RuntimeError('CV convergence failure; do not accept a partial fit')
        rows.append({'candidate':i,'model':name,'parameters':json.dumps(params),'mean_cv_ap':float(scores['test_ap'].mean()),'sd_cv_ap':float(scores['test_ap'].std()),
                     'mean_cv_auc':float(scores['test_auc'].mean()),'mean_cv_brier':float(-scores['test_brier'].mean()),'mean_training_fold_ap':float(scores['train_ap'].mean()),
                     'fold_validation_ap':json.dumps(scores['test_ap'].tolist())})
        candidates.append((name,params,pipe))
        print(f'CV candidate {i}: {name} {params}; AP={rows[-1]["mean_cv_ap"]:.6f}',flush=True)
    table=pd.DataFrame(rows);table.to_csv(out/'training_cv_search.csv',index=False)
    val_rows=[];pred=pd.DataFrame({'user_id':va.index,'y_true':yv.to_numpy()});selected_candidates={}
    for name in NAMES:
        best=table[table.model==name].sort_values(['mean_cv_ap','candidate'],ascending=[False,True]).iloc[0];idx=int(best.candidate)
        _,params,pipe=candidates[idx]
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always');pipe.fit(xt,yt)
        if any(issubclass(w.category,ConvergenceWarning) for w in ws):raise RuntimeError('Final training fit did not converge')
        probability=pipe.predict_proba(xv)[:,list(pipe.classes_).index(1)]
        train_probability=pipe.predict_proba(xt)[:,list(pipe.classes_).index(1)]
        joblib.dump(pipe,run/f'{name}.joblib')
        np.testing.assert_array_equal(joblib.load(run/f'{name}.joblib').predict_proba(xv),pipe.predict_proba(xv))
        result=binary_metrics(yv,probability,cfg['threshold']);result['confusion_unit']='records'
        training=binary_metrics(yt,train_probability,cfg['threshold']);training['confusion_unit']='records'
        val_rows.append({'model':name,**{k:result[k] for k in ['n','positive_rate','threshold']+cfg['report_metrics']},'training_ap':training['average_precision'],
                         'training_brier':training['brier'],'train_validation_ap_gap':training['average_precision']-result['average_precision'],'cv_ap_sd':float(best.sd_cv_ap)})
        selected_candidates[name]={'parameters':params,'full_estimator_parameters':pipe['classifier'].get_params(),'cv_candidate':idx,'validation':result,'training':training}
        pred[name]=probability
    comparison=pd.DataFrame(val_rows).set_index('model',drop=False);policy=cfg['selection_rule']
    eligible=comparison[comparison.average_precision>=comparison.average_precision.max()-policy['ap_tolerance']]
    eligible=eligible[eligible.brier<=eligible.brier.min()+policy['brier_tolerance']]
    selected=next(n for n in NAMES if n in eligible.index)
    comparison.to_csv(out/'validation_comparison.csv',index=False);pred.to_csv(out/'validation_predictions.csv',index=False)
    write_json(out/'development_metrics.json',selected_candidates)
    freeze={'frozen_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),'selected_model':selected,'threshold':cfg['threshold'],'calibration':'none',
            'features':schema['features'],'protocol_sha256':sha256(ROOT/'config/kaggle_experiment.json'),'source_sha256':sha256(Path(__file__)),
            'schema_sha256':cfg['schema_sha256'],'data_sha256':cfg['data_sha256'],'split_sha256':sha256(ROOT/cfg['split_file']),
            'run_dir':str(run.relative_to(ROOT)),'output_dir':str(out.relative_to(ROOT)),'artifact_sha256':{n:sha256(run/f'{n}.joblib') for n in NAMES},
            'comparators_prespecified':NAMES,'selection_rule':policy,'parameters':{n:selected_candidates[n]['parameters'] for n in NAMES},'fit_population':'train only','test_evaluated_at_freeze':False}
    write_json(run/'frozen.json',freeze)
    write_json(out/'freeze_receipt.json',{'frozen_sha256':sha256(run/'frozen.json'),'development_files_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file()}})
    print('FROZEN BEFORE TEST:',selected,flush=True)
    return freeze


def verify_development(run_dir,output_dir):
    cfg=read_json('config/kaggle_experiment.json');run=ROOT/run_dir;out=ROOT/output_dir;freeze=read_json(run/'frozen.json');receipt=read_json(out/'freeze_receipt.json')
    assert sha256(run/'frozen.json')==receipt['frozen_sha256']
    for p,h in receipt['development_files_sha256'].items():assert sha256(out/p)==h,p
    for n,h in freeze['artifact_sha256'].items():assert sha256(run/f'{n}.joblib')==h,n
    assert sha256(Path(__file__))==freeze['source_sha256']
    assert sha256(ROOT/'config/kaggle_experiment.json')==freeze['protocol_sha256']
    assert sha256(ROOT/cfg['split_file'])==freeze['split_sha256']
    return freeze


def evaluate(run_dir=DEFAULT_RUN,output_dir=DEFAULT_OUT):
    freeze=verify_development(run_dir,output_dir);cfg,schema,frame,_=load_data();split=get_split(frame,cfg);out=ROOT/output_dir;run=ROOT/run_dir
    if (out/'test_metrics.json').exists():raise FileExistsError('Formal test results already exist; verify instead of reselecting')
    te=frame.loc[split['test']];x=te[schema['features']];y=te.default_flag.to_numpy();predictions={};results={};pred=pd.DataFrame({'user_id':te.index,'y_true':y})
    for name in freeze['comparators_prespecified']:
        pipe=joblib.load(run/f'{name}.joblib');p=pipe.predict_proba(x)[:,list(pipe.classes_).index(1)];predictions[name]=p
        results[name]=binary_metrics(y,p,freeze['threshold']);results[name]['confusion_unit']='records'
        pred[name+'_probability']=p;pred[name+'_prediction']=(p>=freeze['threshold']).astype(int)
    pred.to_csv(out/'test_predictions.csv',index=False);write_json(out/'test_metrics.json',results)
    intervals,paired,draws,indices=paired_bootstrap(y,predictions,**cfg['bootstrap_kwargs'] if 'bootstrap_kwargs' in cfg else {'replicates':cfg['bootstrap']['replicates'],'seed':cfg['bootstrap']['seed'],'threshold':cfg['threshold'],'minimum_valid_fraction':cfg['bootstrap']['minimum_valid_fraction']})
    write_json(out/'bootstrap_intervals.json',intervals);write_json(out/'paired_lr_minus_comparators.json',paired)
    np.savez_compressed(out/'bootstrap_indices.npz',indices=indices)
    pd.DataFrame([{'replicate':i,'model':n,**{k:float(a[i]) if np.isfinite(a[i]) else None for k,a in ds.items()}} for n,ds in draws.items() for i in range(cfg['bootstrap']['replicates'])]).to_csv(out/'bootstrap_draws.csv',index=False)
    pd.DataFrame([{'model':n,**{k:v for k,v in r.items() if k not in ['na_reasons','confusion_matrix_tn_fp_fn_tp']}} for n,r in results.items()]).to_csv(out/'test_comparison.csv',index=False)
    cal=[]
    for n,p in predictions.items():cal.extend({'model':n,**row} for row in calibration_bins(y,p,bins=10,small_n=30))
    pd.DataFrame(cal).to_csv(out/'test_calibration_bins.csv',index=False)
    render(out,freeze)
    write_json(out/'evaluation_manifest.json',{'evaluated_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),'selected_model':freeze['selected_model'],
               'frozen_sha256':sha256(run/'frozen.json'),'test_policy':'All prespecified models evaluated; no post-test reselection/refit/calibration/threshold change',
               'uncertainty':cfg['bootstrap'],'files_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file()}})
    print(json.dumps(results,indent=2),flush=True)
    return results


def render(out,freeze):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'outputs/.mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve,precision_recall_curve
    pred=pd.read_csv(out/'test_predictions.csv');results=read_json(out/'test_metrics.json');cal=pd.read_csv(out/'test_calibration_bins.csv')
    colors={'dummy':'#68737d','logistic_regression':'#176b87','random_forest':'#c58223'};styles={'dummy':':','logistic_regression':'-','random_forest':'--'}
    fig,axes=plt.subplots(1,3,figsize=(13,4.6),layout='constrained')
    for n in NAMES:
        p=pred[n+'_probability'];fpr,tpr,_=roc_curve(pred.y_true,p);precision,recall,_=precision_recall_curve(pred.y_true,p)
        axes[0].plot(fpr,tpr,color=colors[n],ls=styles[n],label=n)
        axes[1].plot(recall,precision,color=colors[n],ls=styles[n],label=n)
        g=cal[(cal.model==n)&(cal.n>0)];axes[2].plot(g.mean_prediction,g.observed_rate,'o',color=colors[n],label=n,markersize=4)
    axes[0].plot([0,1],[0,1],':',color='#333333');axes[1].axhline(pred.y_true.mean(),ls=':',color='#333333');axes[2].plot([0,1],[0,1],':',color='#333333')
    for ax,title,xlab,ylab in zip(axes,['ROC','Precision–recall','Calibration: 10 equal-width bins'],['False positive rate','Recall','Mean estimated probability'],['True positive rate','Precision','Observed recorded-flag share']):
        ax.set(title=title,xlabel=xlab,ylabel=ylab,xlim=(0,1),ylim=(0,1));ax.legend(fontsize=7);ax.spines[['top','right']].set_visible(False)
    fig.suptitle(f'Independent Kaggle recorded-label experiment | locked test n = {len(pred):,}')
    fig.supxlabel('Origin and default window unverified; no real-world default or Australian validation claim.',fontsize=9)
    fig.savefig(out/'test_curves.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(11,3.8),layout='constrained')
    for ax,n in zip(axes,NAMES):
        cm=np.asarray(results[n]['confusion_matrix_tn_fp_fn_tp']).reshape(2,2).astype(int);ax.imshow(cm,cmap='Blues',vmin=0,vmax=len(pred))
        for i,j in itertools.product(range(2),repeat=2):ax.text(j,i,str(cm[i,j]),ha='center',va='center',fontsize=13)
        ax.set(xticks=[0,1],yticks=[0,1],xlabel='Predicted flag (threshold 0.5)',ylabel='Recorded flag',title=n)
    fig.suptitle('Confusion matrices | units: file records');fig.savefig(out/'test_confusion_matrices.png',dpi=180);plt.close(fig)


def verify(run_dir=DEFAULT_RUN,output_dir=DEFAULT_OUT):
    freeze=verify_development(run_dir,output_dir);out=ROOT/output_dir;m=read_json(out/'evaluation_manifest.json')
    assert m['frozen_sha256']==sha256(ROOT/run_dir/'frozen.json')
    for p,h in m['files_sha256'].items():assert sha256(out/p)==h,p
    print('PASS: independent protocol, split, artifacts, pre-test freeze and evaluation outputs verified.')
    return freeze

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['train','evaluate','verify'],required=True);p.add_argument('--run-dir',default=DEFAULT_RUN);p.add_argument('--output-dir',default=DEFAULT_OUT);a=p.parse_args()
    {'train':train,'evaluate':evaluate,'verify':verify}[a.phase](a.run_dir,a.output_dir)
