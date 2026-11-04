"""Bounded train-only search, validation selection and stage-five freeze."""
import argparse
import json
import platform
import shutil
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate
from sklearn.metrics import log_loss
from .common import ROOT, read_json, write_json, sha256
from .preprocessing import build_pipeline, map_target
from .evaluate_model import metrics


def development_data():
    cfg=read_json('config/model_config.json')
    split=read_json('data/splits/cfpb_split_ids.json')
    assert sha256(ROOT/cfg['data_path'])==split['data_sha256']
    assert sha256(ROOT/'config/label_mapping.json')==split['label_mapping_sha256']
    groups=[set(split[k]) for k in ['train','validation','test']]
    assert not any(groups[i]&groups[j] for i in range(3) for j in range(i+1,3))
    # Subset before mapping labels; test responses are never used by this workflow.
    dev=pd.read_csv(ROOT/cfg['data_path']).set_index('PUF_ID')
    dev=dev.loc[split['train']+split['validation']]
    cols=list(read_json('config/feature_schema.json')['features'])
    y=map_target(dev.ENDSMEET).astype(int)
    return dev.loc[split['train'],cols], y.loc[split['train']], dev.loc[split['validation'],cols], y.loc[split['validation']],dev.loc[split['validation'],'finalwt'],split


def select_finalist(results,cfg):
    names=cfg['complexity_preference']
    best=max(results[n]['validation']['average_precision'] for n in names)
    eligible=[n for n in names if results[n]['validation']['average_precision']>=best-cfg['finalist_ap_tolerance']]
    brier=min(results[n]['validation']['brier'] for n in eligible)
    tied=[n for n in eligible if results[n]['validation']['brier']<=brier+cfg['finalist_brier_tolerance']]
    return tied[0],{'best_ap':best,'ap_eligible':eligible,'best_eligible_brier':brier,'brier_eligible':tied}


def compare(output_dir='models/cfpb/stage4_v1'):
    out=ROOT/output_dir
    if out.exists():raise FileExistsError(f'Preserve existing run {out}; choose a new --output-dir.')
    out.mkdir(parents=True)
    start=time.perf_counter(); cfg=read_json('config/stage4_search.json')
    write_json(out/'search_config.json',cfg)
    def status(stage):
        write_json(out/'status.json',{'stage':stage,'updated_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),'test_evaluated':False})
        print(stage,flush=True)
    status('Checking existing baselines')
    protected=[ROOT/'data/raw/cfpb/NFWBS_PUF_2016_data.csv',ROOT/'data/splits/cfpb_split_ids.json',*list((ROOT/'config').glob('*.json')),*list((ROOT/'models/cfpb/stage3_v2').iterdir())]
    before={str(p.relative_to(ROOT)):sha256(p) for p in protected if p.is_file()}
    xt,yt,xv,yv,wv,split=development_data()
    baseline=ROOT/'models/cfpb/stage3_v2'
    manifest=read_json('models/cfpb/stage3_v2/run_manifest.json')
    for name,h in manifest['artifacts_sha256'].items():assert sha256(baseline/name)==h
    for name in ['model_config','feature_schema','label_mapping']:
        assert sha256(ROOT/f'config/{name}.json')==sha256(baseline/f'{name}.json')
    saved=pd.read_csv(baseline/'validation_predictions.csv')
    np.testing.assert_array_equal(saved.PUF_ID,xv.index)
    objects={n:joblib.load(baseline/f'{n}.joblib') for n in ['dummy','logistic_regression']}
    for n,obj in objects.items():np.testing.assert_allclose(obj.predict_proba(xv)[:,1],saved[n],atol=1e-14,rtol=0)
    cv=StratifiedKFold(cfg['cv_folds'],shuffle=True,random_state=cfg['seed'])
    write_json(out/'cv_fold_ids.json',[{'fit_ids':xt.index[a].tolist(),'heldout_ids':xt.index[b].tolist()} for a,b in cv.split(xt,yt)])
    status('Searching four RF configurations with training-only five-fold CV')
    search=GridSearchCV(build_pipeline(RandomForestClassifier(**cfg['rf_fixed'])),cfg['rf_grid'],scoring={'ap':'average_precision','auc':'roc_auc','brier':'neg_brier_score'},refit=False,cv=cv,n_jobs=1,return_train_score=True,error_score='raise')
    search.fit(xt,yt)
    table=pd.DataFrame(search.cv_results_);table.to_csv(out/'rf_cv_results.csv',index=False)
    top=table.mean_test_ap.max()
    choices=[i for i in table.index if table.loc[i,'mean_test_ap']>=top-cfg['rf_cv_tie_tolerance']]
    chosen=min(choices,key=lambda i:(0 if table.loc[i,'params']['classifier__max_depth']==6 else 1,-table.loc[i,'params']['classifier__min_samples_leaf']))
    params=table.loc[chosen,'params']
    write_json(out/'rf_choice.json',{'cv_result_row':int(chosen),'params':params,'best_cv_mean_ap':float(top),'chosen_cv_mean_ap':float(table.loc[chosen,'mean_test_ap'])})
    forest=clone(search.estimator).set_params(**params).fit(xt,yt)
    objects['random_forest']=forest
    joblib.dump(forest,out/'random_forest.joblib')
    status('Fitting train-only out-of-fold sigmoid calibration for LR and RF')
    for name,base in [('logistic_sigmoid',objects['logistic_regression']),('forest_sigmoid',forest)]:
        obj=CalibratedClassifierCV(clone(base),method='sigmoid',cv=StratifiedKFold(5,shuffle=True,random_state=42),ensemble=False,n_jobs=1)
        obj.fit(xt,yt);objects[name]=obj;joblib.dump(obj,out/f'{name}.joblib')
    status('Measuring validation finalists and fixed-parameter development stability')
    results={};pred=pd.DataFrame({'PUF_ID':xv.index,'y_true':yv.to_numpy()});reliability=[]; stability_rows=[]
    outer=StratifiedKFold(cfg['stability_folds'],shuffle=True,random_state=cfg['stability_seed'])
    write_json(out/'stability_fold_ids.json',[{'fit_ids':xt.index[a].tolist(),'heldout_ids':xt.index[b].tolist()} for a,b in outer.split(xt,yt)])
    for name,obj in objects.items():
        p=obj.predict_proba(xv)[:,1];pt=obj.predict_proba(xt)[:,1]
        pred[name]=p
        result={'validation':metrics(yv,p,cfg['threshold']),'train_apparent':metrics(yt,pt,cfg['threshold']),'validation_finalwt_sensitivity':metrics(yv,p,cfg['threshold'],wv),'validation_log_loss':float(log_loss(yv,p)),'validation_mean_probability':float(p.mean())}
        result['ap_train_minus_validation']=result['train_apparent']['average_precision']-result['validation']['average_precision']
        result['brier_validation_minus_train']=result['validation']['brier']-result['train_apparent']['brier']
        # Calibration is nested inside each outer training fold; RF parameters are fixed here.
        scores=cross_validate(clone(obj),xt,yt,cv=outer,scoring={'ap':'average_precision','auc':'roc_auc','brier':'neg_brier_score'},n_jobs=1,error_score='raise')
        result['training_cv_stability']={k:{'mean':float(np.mean(scores['test_'+k])),'sd':float(np.std(scores['test_'+k],ddof=1)),'folds':scores['test_'+k].tolist()} for k in ['ap','auc','brier']}
        for i in range(3):stability_rows.append({'model':name,'fold':i,'ap':float(scores['test_ap'][i]),'auc':float(scores['test_auc'][i]),'brier':float(-scores['test_brier'][i])})
        result['training_cv_stability']['brier_note']='Values above use sklearn negative-Brier scoring; positive Brier is in stability.csv.'
        bins=pd.qcut(pd.Series(p),q=10,duplicates='drop') if np.unique(p).size>1 else pd.Series(['constant']*len(p))
        frame=pd.DataFrame({'p':p,'y':yv.to_numpy(),'bin':bins})
        for group,g in frame.groupby('bin',observed=True):reliability.append({'model':name,'bin':str(group),'n':len(g),'mean_prediction':float(g.p.mean()),'observed_rate':float(g.y.mean())})
        results[name]=result
        if name in ['dummy','logistic_regression']:shutil.copy2(baseline/f'{name}.joblib',out/f'{name}.joblib')
        np.testing.assert_allclose(joblib.load(out/f'{name}.joblib').predict_proba(xv)[:,1],p,atol=1e-14,rtol=0)
        write_json(out/'comparison.json',results)
        print(f'{name}: AP={result["validation"]["average_precision"]:.6f}, Brier={result["validation"]["brier"]:.6f}',flush=True)
    pred.to_csv(out/'validation_predictions.csv',index=False)
    pd.DataFrame(reliability).to_csv(out/'validation_reliability_bins.csv',index=False)
    pd.DataFrame(stability_rows).to_csv(out/'stability.csv',index=False)
    comparison=pd.DataFrame([{'model':n,**r['validation'],'train_ap':r['train_apparent']['average_precision'],'train_brier':r['train_apparent']['brier'],'ap_gap':r['ap_train_minus_validation'],'train_cv_ap_mean':r['training_cv_stability']['ap']['mean'],'train_cv_ap_sd':r['training_cv_stability']['ap']['sd']} for n,r in results.items()])
    comparison.to_csv(out/'validation_comparison.csv',index=False)
    selected,trace=select_finalist(results,cfg)
    for n in ['feature_schema','label_mapping','model_config']:shutil.copy2(ROOT/f'config/{n}.json',out/f'{n}.json')
    frozen={'version':'stage5-frozen-v1','selected_model':selected,'artifact':str((out/f'{selected}.joblib').relative_to(ROOT)),'artifact_sha256':sha256(out/f'{selected}.joblib'),'data_sha256':before['data/raw/cfpb/NFWBS_PUF_2016_data.csv'],'split_sha256':before['data/splits/cfpb_split_ids.json'],'schema_sha256':sha256(ROOT/'config/feature_schema.json'),'label_mapping_sha256':sha256(ROOT/'config/label_mapping.json'),'features':list(xt.columns),'threshold':cfg['threshold'],'threshold_rule':'Fixed 0.5 reference; no business cost function or threshold optimization.','calibration':'sigmoid, train-only 5-fold OOF, ensemble=False' if 'sigmoid' in selected else 'none','parameters':str(objects[selected].get_params(deep=False)),'selection_trace':trace,'fit_population':'Original train only (3810); no train+validation refit','test_evaluated':False,'stage5_policy':'Evaluate frozen artifact once on locked test IDs. Do not reselect from test metrics. Retain sample-level scope; report weighted sensitivity separately.'}
    write_json(out/'frozen_selection.json',frozen)
    assert all(sha256(ROOT/p)==h for p,h in before.items())
    write_json(out/'run_manifest.json',{'completed_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),'python':sys.version,'platform':platform.platform(),'elapsed_seconds':time.perf_counter()-start,'protected_sha256':before,'source_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'src').glob('*.py')},'test_evaluated':False,'artifacts_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file() and p.name!='status.json'}})
    status('COMPLETE; selected '+selected)
    print(comparison[['model','average_precision','roc_auc','brier','precision','recall','f1']].to_string(index=False),flush=True)
    return frozen

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',default='models/cfpb/stage4_v1');args=parser.parse_args();compare(args.output_dir)
