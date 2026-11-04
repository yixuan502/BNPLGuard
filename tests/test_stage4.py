"""Stage-four isolation, selection and frozen-object acceptance checks."""
import joblib
import numpy as np
import pandas as pd
from src.common import ROOT, read_json, sha256
from src.compare_models import select_finalist, development_data
from src.evaluate_model import metrics

OUT=ROOT/'models/cfpb/stage4_v1'

def test_inner_and_stability_folds_never_use_validation_or_test():
    split=read_json('data/splits/cfpb_split_ids.json')
    train=set(split['train']); forbidden=set(split['validation'])|set(split['test'])
    for path in ['cv_fold_ids.json','stability_fold_ids.json']:
        seen=[]
        for fold in read_json(OUT/path):
            a,b=set(fold['fit_ids']),set(fold['heldout_ids'])
            assert not a&b and a|b==train
            assert not (a|b)&forbidden
            seen.extend(b)
        assert set(seen)==train and len(seen)==len(train)

def test_selection_policy_uses_predeclared_tolerances():
    cfg=read_json('config/stage4_search.json')
    names=cfg['complexity_preference']
    def r(ap,brier):return {'validation':{'average_precision':ap,'brier':brier}}
    results=dict(zip(names,[r(.72,.16),r(.72,.159),r(.725,.159),r(.725,.158)]))
    assert select_finalist(results,cfg)[0]=='logistic_regression'
    results['random_forest']=r(.75,.15)
    assert select_finalist(results,cfg)[0]=='random_forest'

def test_calibration_wraps_full_pipeline_and_uses_train_cv():
    for name in ['logistic_sigmoid','forest_sigmoid']:
        obj=joblib.load(OUT/f'{name}.joblib')
        assert obj.ensemble is False and obj.method=='sigmoid' and obj.cv.n_splits==5
        assert list(obj.estimator.named_steps)==['codebook','preprocessor','classifier']
        assert len(obj.calibrated_classifiers_)==1

def test_saved_predictions_metrics_and_frozen_selection():
    xt,yt,xv,yv,wv,split=development_data()
    saved=pd.read_csv(OUT/'validation_predictions.csv')
    np.testing.assert_array_equal(saved.PUF_ID,xv.index)
    results=read_json(OUT/'comparison.json')
    for name,r in results.items():
        obj=joblib.load(OUT/f'{name}.joblib');p=obj.predict_proba(xv)[:,1]
        np.testing.assert_allclose(saved[name],p,rtol=0,atol=1e-14)
        actual=metrics(yv,p,.5)
        for key in ['average_precision','roc_auc','brier','precision','recall','f1']:
            assert actual[key]==r['validation'][key]
    frozen=read_json(OUT/'frozen_selection.json')
    assert select_finalist(results,read_json('config/stage4_search.json'))[0]==frozen['selected_model']
    assert sha256(ROOT/frozen['artifact'])==frozen['artifact_sha256']
    assert frozen['test_evaluated'] is False and frozen['threshold']==.5
    manifest=read_json(OUT/'run_manifest.json')
    assert all(sha256(ROOT/p)==h for p,h in manifest['protected_sha256'].items())
