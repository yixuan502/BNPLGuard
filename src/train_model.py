"""Reproducible train/validation baselines with locked, unevaluated test IDs."""
import argparse
import json
import platform
import sys
import time
import warnings
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from importlib.metadata import version
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.exceptions import ConvergenceWarning
from .common import ROOT, read_json, write_json, sha256
from .data_audit import audit
from .preprocessing import map_target, build_pipeline
from .evaluate_model import metrics

def fixed_splits(ids, labels, data_hash, cfg):
    path=ROOT/'data/splits/cfpb_split_ids.json'
    if path.exists():
        saved=json.loads(path.read_text())
        if saved['data_sha256']!=data_hash or saved['seed']!=cfg['seed'] or saved['label_mapping_sha256']!=sha256(ROOT/'config/label_mapping.json'):
            raise ValueError('Locked split provenance changed; do not silently regenerate it.')
    else:
        dev,test=train_test_split(ids,test_size=cfg['test_fraction'],stratify=labels.loc[ids],random_state=cfg['seed'])
        train,val=train_test_split(dev,test_size=cfg['validation_fraction']/(1-cfg['test_fraction']),stratify=labels.loc[dev],random_state=cfg['seed'])
        saved={'data_sha256':data_hash,'seed':cfg['seed'],'label_mapping_sha256':sha256(ROOT/'config/label_mapping.json'),'policy':'Frozen test IDs, no test metrics until stage 5','train':list(map(int,train)),'validation':list(map(int,val)),'test':list(map(int,test))}
        write_json(path,saved)
    groups=[set(saved[s]) for s in ['train','validation','test']]
    if any(groups[i]&groups[j] for i in range(3) for j in range(i+1,3)) or set.union(*groups)!=set(ids):
        raise ValueError('Splits overlap or fail complete eligible-ID coverage')
    if any(len(saved[s])!=len(set(saved[s])) for s in ['train','validation','test']):
        raise ValueError('Repeated ID within split')
    return saved

def train(output_dir=None):
    audit()
    cfg=read_json('config/model_config.json')
    df=pd.read_csv(ROOT/cfg['data_path']).set_index('PUF_ID',drop=False)
    y=map_target(df.ENDSMEET)
    ids=y.index[y.notna()]
    split=fixed_splits(ids,y,sha256(ROOT/cfg['data_path']),cfg)
    # Deliberately extract only train and validation rows. Test set is never passed to a model.
    tr=df.loc[split['train']]; va=df.loc[split['validation']]
    columns=list(read_json('config/feature_schema.json')['features'])
    xt=tr[columns]; xv=va[columns]
    yt=y.loc[tr.index].astype(int); yv=y.loc[va.index].astype(int)
    out=Path(output_dir) if output_dir else ROOT/'models/cfpb/stage3_v2'
    if not out.is_absolute(): out=ROOT/out
    out.mkdir(parents=True,exist_ok=True)
    marker=out/'run_manifest.json'
    if marker.exists():
        raise FileExistsError(f'Completed run preserved: {out}. Use --output-dir for a new reproducibility run.')
    result={}
    predictions=pd.DataFrame({'PUF_ID':va.index,'y_true':yv.to_numpy()})
    for name,estimator in [('dummy',DummyClassifier(**cfg['dummy'])),('logistic_regression',LogisticRegression(**cfg['logistic_regression'],random_state=cfg['seed']))]:
        pipe=build_pipeline(estimator)
        start=time.perf_counter()
        with warnings.catch_warnings(record=True) as recorded:
            warnings.simplefilter('always')
            pipe.fit(xt,yt)
        if any(issubclass(w.category,ConvergenceWarning) for w in recorded):
            raise RuntimeError('Logistic regression did not converge; inspect solver before acceptance')
        probability=pipe.predict_proba(xv)[:,1]
        fit_seconds=time.perf_counter()-start
        joblib.dump(pipe,out/f'{name}.joblib')
        # Verify persisted artifact, not merely the in-memory estimator.
        np.testing.assert_allclose(joblib.load(out/f'{name}.joblib').predict_proba(xv)[:,1],probability,rtol=0,atol=0)
        predictions[name]=probability
        result[name]={'validation':metrics(yv,probability,cfg['threshold']),
            'validation_finalwt_sensitivity':metrics(yv,probability,cfg['threshold'],va.finalwt),
            'fit_and_predict_seconds':fit_seconds,'fit_warnings':[str(w.message) for w in recorded],
            'iterations':pipe['classifier'].n_iter_.tolist() if hasattr(pipe['classifier'],'n_iter_') else None,
            'train_n':len(tr),'train_positive_rate':float(yt.mean())}
    predictions.to_csv(out/'validation_predictions.csv',index=False)
    write_json(out/'validation_metrics.json',result)
    for name in ['model_config','feature_schema','label_mapping']:
        write_json(out/f'{name}.json',read_json(f'config/{name}.json'))
    manifest={'run_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),'python':sys.version,'platform':platform.platform(),
        'dependencies':{p:version(p) for p in ['numpy','pandas','scikit-learn','joblib','scipy']},
        'data_sha256':sha256(ROOT/cfg['data_path']),'split_sha256':sha256(ROOT/'data/splits/cfpb_split_ids.json'),
        'code_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'src').glob('*.py')},
        'config_sha256':{str(p.relative_to(ROOT)):sha256(p) for p in (ROOT/'config').glob('*.json')},
        'split_n':{s:len(split[s]) for s in ['train','validation','test']},'test_evaluated':False,
        'selection':'Stage 3 baselines only; no final deployment model selected','artifacts_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file()}}
    write_json(marker,manifest)
    if output_dir is None:
        write_json('outputs/metrics/validation_baselines.json',result)
        pd.DataFrame([{'model':name,**r['validation']} for name,r in result.items()]).to_csv(ROOT/'outputs/tables/validation_baselines.csv',index=False)
    print(json.dumps({name:r['validation'] for name,r in result.items()},indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',help='New run directory; completed artifacts are never overwritten')
    args=parser.parse_args()
    train(args.output_dir)
