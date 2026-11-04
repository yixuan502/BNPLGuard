"""Independent numerical checks before using the locked test labels."""
import numpy as np
import pytest
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,accuracy_score,precision_score,recall_score,f1_score
from src.evaluation_stats import binary_metrics,paired_bootstrap,calibration_bins,wilson_interval

@pytest.mark.parametrize('weighted',[False,True])
def test_fast_metrics_match_independent_sklearn_with_ties(weighted):
    rng=np.random.default_rng(4);y=rng.integers(0,2,143);p=np.round(rng.random(143),1)
    w=rng.uniform(.2,3,143) if weighted else None
    r=binary_metrics(y,p,weights=w);pred=p>=.5
    expected={'average_precision':average_precision_score(y,p,sample_weight=w),'roc_auc':roc_auc_score(y,p,sample_weight=w),'brier':brier_score_loss(y,p,sample_weight=w),'accuracy':accuracy_score(y,pred,sample_weight=w),'precision':precision_score(y,pred,sample_weight=w),'recall':recall_score(y,pred,sample_weight=w),'f1':f1_score(y,pred,sample_weight=w)}
    for key,value in expected.items():assert r[key]==pytest.approx(value,abs=1e-12)

def test_undefined_metrics_and_illegal_probabilities():
    no=binary_metrics([0,0],[.1,.1]);assert no['precision'] is None and no['recall'] is None and no['roc_auc'] is None and no['average_precision'] is None and no['f1'] is None
    yes=binary_metrics([1,1],[.3,.7]);assert yes['roc_auc'] is None and yes['false_positive_rate'] is None and yes['average_precision']==1
    with pytest.raises(ValueError):binary_metrics([0,1],[.2,np.inf])
    with pytest.raises(ValueError):binary_metrics([0,1],[-.1,.5])

def test_paired_bootstrap_identical_models_and_seed():
    y=np.array([0,0,1,1,0,1]);p=np.array([.1,.2,.4,.7,.5,.8])
    a=paired_bootstrap(y,{'logistic_regression':p,'dummy':p.copy()},40,12)
    b=paired_bootstrap(y,{'logistic_regression':p,'dummy':p.copy()},40,12)
    np.testing.assert_array_equal(a[3],b[3])
    for metric in ['average_precision','roc_auc','brier']:
        assert a[1]['dummy'][metric]['lower']==0 and a[1]['dummy'][metric]['upper']==0
    for i,idx in enumerate(a[3]):
        value=binary_metrics(y[idx],p[idx])['brier'];assert a[2]['logistic_regression']['brier'][i]==value

def test_bootstrap_reports_all_undefined_precision():
    cis,paired,draws,indices=paired_bootstrap(np.array([0,0,1,1]),{'dummy':np.full(4,.25)},20,33)
    assert cis['dummy']['precision']['valid_replicates']==0 and cis['dummy']['precision']['lower'] is None
    assert cis['dummy']['roc_auc']['invalid_replicates']>0

def test_calibration_endpoints_counts_and_empty_bins():
    rows=calibration_bins([0,1,1],[0.,.1,1.])
    assert sum(r['n'] for r in rows)==3
    assert rows[0]['n']==1 and rows[1]['n']==1 and rows[9]['n']==1
    assert rows[2]['observed_rate'] is None
    assert wilson_interval(0,0)==(None,None)
    assert wilson_interval(0,10)[0]==0
    assert wilson_interval(10,10)[1]==pytest.approx(1)
