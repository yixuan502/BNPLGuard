"""Formal evaluation of immutable fitted artifacts. No model fitting or selection."""
import argparse
import json
import platform
import shutil
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_curve, precision_recall_curve
from .common import ROOT, read_json, write_json, sha256
from .preprocessing import clean_features, map_target
from .evaluation_stats import binary_metrics,paired_bootstrap,calibration_bins,wilson_interval,CI_METRICS


def now(): return datetime.now(ZoneInfo('Australia/Sydney')).isoformat()


def preflight():
    freeze=read_json('config/stage5_frozen.json');plan=read_json('config/stage5_evaluation.json')
    if Path(sys.prefix)!=ROOT/'.venv':raise ValueError('Use the active project .venv')
    assert freeze['selected_model']==plan['selected']=='logistic_regression'
    assert freeze['calibration']=='none' and freeze['threshold']==plan['threshold']==.5
    cfg=read_json('config/model_config.json');schema=read_json('config/feature_schema.json')
    for rel,key in [(cfg['data_path'],'data_sha256'),('data/splits/cfpb_split_ids.json','split_sha256'),('config/feature_schema.json','schema_sha256'),('config/label_mapping.json','label_mapping_sha256')]:
        assert sha256(ROOT/rel)==freeze[key],rel
    assert sha256(ROOT/freeze['artifact'])==freeze['artifact_sha256']
    split=read_json('data/splits/cfpb_split_ids.json'); sets=[set(split[k]) for k in ['train','validation','test']]
    assert [len(s) for s in sets]==[3810,1270,1270]
    assert all(len(split[k])==len(set(split[k])) for k in ['train','validation','test'])
    assert not any(sets[i]&sets[j] for i in range(3) for j in range(i+1,3))
    directory=ROOT/plan['model_directory'];old=read_json(directory/'run_manifest.json')
    for rel,h in old['protected_sha256'].items():assert sha256(ROOT/rel)==h,rel
    for rel,h in old['artifacts_sha256'].items():assert sha256(directory/rel)==h,rel
    for rel in ['src/preprocessing.py','src/train_model.py','src/common.py']:
        assert sha256(ROOT/rel)==old['source_sha256'][rel],rel
    raw=pd.read_csv(ROOT/cfg['data_path']).set_index('PUF_ID',drop=False)
    assert raw.index.is_unique and not raw.index.isna().any()
    # Membership/eligibility only, never a performance calculation.
    eligible=set(raw.index[raw.ENDSMEET.isin([1,2,3])]);assert set.union(*sets)==eligible
    features=list(schema['features']); assert features==freeze['features']
    train=raw.loc[split['train'],features];clean=clean_features(train)
    modes=np.array([clean[c].mode().min() for c in features]); filled=clean.fillna(dict(zip(features,modes)))
    models={};evidence={}
    for name in [plan['selected'],*plan['comparators']]:
        path=directory/f'{name}.joblib';obj=joblib.load(path)
        assert list(obj.named_steps)==['codebook','preprocessor','classifier']
        assert obj['codebook'].schema==schema['features']
        cat=obj['preprocessor'].named_transformers_['categorical']
        np.testing.assert_array_equal(cat['imputer'].statistics_,modes)
        assert obj['preprocessor'].transformers_[0][2]==features
        for j,col in enumerate(features):np.testing.assert_array_equal(cat['onehot'].categories_[j],np.unique(filled[col]))
        np.testing.assert_array_equal(obj.classes_,[0,1])
        if name=='logistic_regression':assert obj['classifier'].get_params()==freeze['parameters']
        if name=='random_forest':
            params=obj['classifier'].get_params()
            assert all(params[k]==v for k,v in freeze['rf_comparator_parameters'].items())
        if name=='dummy':assert obj['classifier'].strategy=='prior'
        models[name]=obj;evidence[name]={'artifact':str(path.relative_to(ROOT)),'sha256':sha256(path),'training_modes':modes.tolist(),'training_encoder_categories_verified':True,'raw_schema_verified':True}
    protected={str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'config').glob('*.json')}
    protected.update({str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'models/cfpb').rglob('*') if p.is_file()})
    protected[cfg['data_path']]=sha256(ROOT/cfg['data_path']);protected['data/splits/cfpb_split_ids.json']=sha256(ROOT/'data/splits/cfpb_split_ids.json')
    return freeze,plan,split,raw,models,protected,evidence


def subgroup_tables(raw_test,y,predictions,plan):
    records=[]; spec=plan['subgroups']
    for scheme in ['age_primary','age_detailed','income_primary']:
        field='agecat' if scheme.startswith('age') else 'PPINCIMP';groups=dict(spec[scheme])
        known=[code for codes in groups.values() for code in codes]
        masks={name:raw_test[field].isin(codes).to_numpy() for name,codes in groups.items()}
        if (~raw_test[field].isin(known)).any():masks['Unknown']=~raw_test[field].isin(known).to_numpy()
        for label,mask in masks.items():
            for model,p in predictions.items():
                yy=np.asarray(y)[mask];pp=np.asarray(p)[mask]
                if not len(yy):
                    records.append({'scheme':scheme,'group':label,'model':model,'n':0,'positive_n':0,'negative_n':0,'limitations':'Empty group'});continue
                r=binary_metrics(yy,pp,.5);tn,fp,fn,tp=r['confusion_matrix_tn_fp_fn_tp']
                rlo,rhi=wilson_interval(tp,tp+fn);flo,fhi=wilson_interval(fp,fp+tn)
                flags=[]
                if len(yy)<spec['small_group_n']:flags.append('n<100')
                if r['positive_n']<spec['small_class_n']:flags.append('positive n<30')
                if r['negative_n']<spec['small_class_n']:flags.append('negative n<30')
                if len(np.unique(yy))<2:flags.append('one outcome class')
                records.append({'scheme':scheme,'group':label,'model':model,**{k:r[k] for k in ['n','positive_n','negative_n',*CI_METRICS]},'recall_wilson_lower':rlo,'recall_wilson_upper':rhi,'fpr_wilson_lower':flo,'fpr_wilson_upper':fhi,'limitations':'; '.join(flags) or 'Descriptive estimates; no fairness certification','na_reasons':json.dumps(r['na_reasons'])})
    return pd.DataFrame(records)


def verify_run(out):
    manifest=read_json(out/'run_manifest.json')
    for rel,h in manifest['protected_sha256'].items():assert sha256(ROOT/rel)==h,rel
    for rel,h in manifest['output_sha256'].items():assert sha256(out/rel)==h,rel
    print('PASS: fixed artifacts/config/data/split and saved evaluation outputs unchanged.')


def evaluate(output_dir='outputs/evaluation/stage5_v1'):
    out=ROOT/output_dir
    if out.exists():raise FileExistsError(f'Preserve existing evaluation: {out}. Use --verify-only or choose a new output directory.')
    out.mkdir(parents=True)
    freeze,plan,split,raw,models,protected,evidence=preflight()
    source={str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'src').glob('*.py')}
    def status(s):
        write_json(out/'status.json',{'stage':s,'time':now()});print(s,flush=True)
    for name in ['stage5_evaluation','stage5_frozen','feature_schema','label_mapping']:
        shutil.copy2(ROOT/f'config/{name}.json',out/f'{name}.json')
    write_json(out/'pretest_checkpoint.json',{'sealed_at':now(),'source_sha256':source,'plan_sha256':sha256(ROOT/'config/stage5_evaluation.json'),'freeze_sha256':sha256(ROOT/'config/stage5_frozen.json'),'protected_sha256':protected,'models':evidence,'split_sizes':{k:len(split[k]) for k in ['train','validation','test']},'test_scores_computed_at_checkpoint':False})
    status('Preflight passed and evaluation source/plan sealed; scoring locked test rows')
    features=freeze['features'];test=raw.loc[split['test']];x=test[features];y=map_target(test.ENDSMEET).astype(int).to_numpy()
    assert np.isfinite(test.finalwt).all() and (test.finalwt>0).all()
    results={};weighted={};predictions={};rows=pd.DataFrame({'PUF_ID':test.index,'y_true':y,'finalwt':test.finalwt.to_numpy(),'agecat':test.agecat.to_numpy(),'PPINCIMP':test.PPINCIMP.to_numpy()})
    for name,obj in models.items():
        p=obj.predict_proba(x)[:,1]
        np.testing.assert_array_equal(p,obj.predict_proba(x)[:,1])
        np.testing.assert_array_equal(p,joblib.load(ROOT/evidence[name]['artifact']).predict_proba(x)[:,1])
        predictions[name]=p;rows[f'{name}_probability']=p;rows[f'{name}_prediction']=(p>=.5).astype(int)
        results[name]=binary_metrics(y,p,.5);weighted[name]=binary_metrics(y,p,.5,test.finalwt.to_numpy())
    rows.to_csv(out/'test_predictions.csv',index=False)
    write_json(out/'test_metrics.json',results);write_json(out/'weighted_test_sensitivity.json',weighted)
    pd.DataFrame([{'model':n,**{k:v for k,v in r.items() if k not in ['na_reasons','confusion_matrix_tn_fp_fn_tp']},'na_reasons':json.dumps(r['na_reasons'])} for n,r in results.items()]).to_csv(out/'test_metrics.csv',index=False)
    for name,p in predictions.items():
        fpr,tpr,thresholds=roc_curve(y,p);pd.DataFrame({'fpr':fpr,'tpr':tpr,'threshold':thresholds}).to_csv(out/f'{name}_roc.csv',index=False)
        precision,recall,thresholds=precision_recall_curve(y,p)
        pd.DataFrame({'precision':precision,'recall':recall,'threshold':np.r_[thresholds,np.nan]}).to_csv(out/f'{name}_pr.csv',index=False)
    status('Computing 2000 paired fixed-model bootstrap replicates')
    b=plan['bootstrap'];cis,paired,draws,indices=paired_bootstrap(y,predictions,b['replicates'],b['seed'],.5,b['minimum_valid_fraction'])
    for name,fields in cis.items():
        for key,r in fields.items():r['point']=results[name][key];r['na_reason']=results[name]['na_reasons'].get(key)
    for comp,fields in paired.items():
        for key,r in fields.items():r['point']=results['logistic_regression'][key]-results[comp][key];r['direction']='LR minus comparator; negative Brier difference favors LR'
    write_json(out/'bootstrap_intervals.json',cis);write_json(out/'paired_differences.json',paired)
    np.savez_compressed(out/'bootstrap_indices.npz',indices=indices)
    pd.concat([pd.DataFrame({'replicate':np.arange(b['replicates']),'model':name,**ds}) for name,ds in draws.items()]).to_csv(out/'bootstrap_draws.csv',index=False)
    pd.DataFrame([{'model':n,'metric':k,**r} for n,fields in cis.items() for k,r in fields.items()]).to_csv(out/'bootstrap_intervals.csv',index=False)
    cal=calibration_bins(y,predictions['logistic_regression'],plan['calibration']['bins'],plan['calibration']['small_bin_n'])
    pd.DataFrame(cal).to_csv(out/'lr_calibration_bins.csv',index=False)
    occupied=[r for r in cal if r['n']]
    write_json(out/'lr_probability_diagnostics.json',{'n':len(y),'mean_prediction':float(predictions['logistic_regression'].mean()),'observed_positive_rate':float(y.mean()),'mean_prediction_minus_prevalence':float(predictions['logistic_regression'].mean()-y.mean()),'equal_width_binned_absolute_gap':sum(r['n']*abs(r['mean_prediction']-r['observed_rate']) for r in occupied)/len(y),'empty_bins':sum(r['n']==0 for r in cal),'small_bins':[r['bin'] for r in cal if r['n']<30],'note':'Binned absolute gap depends on binning; not a calibration hypothesis test or certificate.'})
    subgroup_tables(test,y,predictions,plan).to_csv(out/'subgroup_metrics.csv',index=False)
    status('Validation-only permutation importance; no model refitting')
    validation=raw.loc[split['validation']];xv=validation[features];yv=map_target(validation.ENDSMEET).astype(int)
    perm=plan['permutation'];importance=permutation_importance(models['logistic_regression'],xv,yv,scoring='average_precision',n_repeats=perm['repeats'],random_state=perm['seed'],n_jobs=1)
    pd.DataFrame({'feature':features,'mean_ap_drop':importance.importances_mean,'sd_ap_drop':importance.importances_std}).sort_values('mean_ap_drop',ascending=False).to_csv(out/'validation_permutation_importance.csv',index=False)
    pd.DataFrame(importance.importances.T,columns=features).to_csv(out/'validation_permutation_repeats.csv',index_label='repeat')
    stability=ROOT/'models/cfpb/stage4_v1/stability.csv';shutil.copy2(stability,out/'stage4_development_stability.csv')
    old=read_json('models/cfpb/stage4_v1/comparison.json')
    delta=[{'model':name,'metric':k,'validation':old[name]['validation'][k],'test':r[k],'test_minus_validation':r[k]-old[name]['validation'][k] if r[k] is not None and old[name]['validation'][k] is not None else None} for name,r in results.items() for k in ['accuracy','precision','recall','f1','roc_auc','average_precision','brier']]
    pd.DataFrame(delta).to_csv(out/'validation_test_deltas.csv',index=False)
    assert all(sha256(ROOT/p)==h for p,h in protected.items())
    assert all(sha256(ROOT/p)==h for p,h in source.items())
    status('COMPLETE: fixed test evaluation and validation explanation saved; selection unchanged')
    write_json(out/'run_manifest.json',{'completed_at':now(),'python':sys.version,'platform':platform.platform(),'selected_model':'logistic_regression','test_evaluated':True,'threshold':.5,'model_refitted':False,'protected_sha256':protected,'source_sha256':source,'output_sha256':{str(p.relative_to(out)):sha256(p) for p in out.rglob('*') if p.is_file() and p.name!='run_manifest.json'}})
    print(pd.DataFrame([{'model':n,**{k:r[k] for k in ['average_precision','roc_auc','brier','precision','recall','f1']}} for n,r in results.items()]).to_string(index=False),flush=True)
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',default='outputs/evaluation/stage5_v1');parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    if args.verify_only:verify_run(ROOT/args.output_dir)
    else:evaluate(args.output_dir)
