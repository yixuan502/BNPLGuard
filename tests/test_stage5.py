"""Frozen-object, statistical and evidence-integrity acceptance checks."""
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss
from src.common import ROOT,read_json,sha256
from src.evaluate_frozen import preflight,verify_run
from src.evaluation_stats import binary_metrics

OUT=ROOT/'outputs/evaluation/stage5_v1'


def test_preflight_cannot_fit_any_pipeline(monkeypatch):
    def forbidden(*args,**kwargs):raise AssertionError('Evaluation must not fit a model')
    monkeypatch.setattr(Pipeline,'fit',forbidden)
    freeze,plan,split,raw,models,protected,evidence=preflight()
    assert freeze['selected_model']=='logistic_regression' and freeze['calibration']=='none'
    assert all('training_encoder_categories_verified' in r for r in evidence.values())
    verify_run(OUT)


def test_frozen_input_contract_and_repeated_inference():
    freeze=read_json('config/stage5_frozen.json');model=joblib.load(ROOT/freeze['artifact'])
    split=read_json('data/splits/cfpb_split_ids.json')
    raw=pd.read_csv(ROOT/'data/raw/cfpb/NFWBS_PUF_2016_data.csv').set_index('PUF_ID')
    x=raw.loc[split['validation'][:5],freeze['features']].copy()
    np.testing.assert_array_equal(model.predict_proba(x),model.predict_proba(x))
    missing=x.astype(float).copy();missing[:]=np.nan
    probability=model.predict_proba(missing)
    assert np.isfinite(probability).all() and ((probability>=0)&(probability<=1)).all()
    np.testing.assert_allclose(probability.sum(axis=1),1)
    with pytest.raises(ValueError):model.predict_proba(x.drop(columns='HOUSING'))
    for invalid in [99999,np.inf,'arbitrary category']:
        bad=x.copy();bad['HOUSING']=invalid
        with pytest.raises(ValueError):model.predict_proba(bad)
    assert model['preprocessor'].named_transformers_['categorical']['onehot'].handle_unknown=='ignore'
    assert sha256(ROOT/freeze['artifact'])==freeze['artifact_sha256']


def test_saved_test_ids_and_sklearn_metrics():
    pred=pd.read_csv(OUT/'test_predictions.csv');split=read_json('data/splits/cfpb_split_ids.json')
    np.testing.assert_array_equal(pred.PUF_ID,split['test'])
    assert not set(pred.PUF_ID)&(set(split['train'])|set(split['validation']))
    report=read_json(OUT/'test_metrics.json')
    for name in ['logistic_regression','dummy','random_forest']:
        p=pred[f'{name}_probability'].to_numpy();r=report[name]
        assert r['average_precision']==pytest.approx(average_precision_score(pred.y_true,p),abs=1e-12)
        assert r['roc_auc']==pytest.approx(roc_auc_score(pred.y_true,p),abs=1e-12)
        assert r['brier']==pytest.approx(brier_score_loss(pred.y_true,p),abs=1e-12)
        np.testing.assert_array_equal(pred[f'{name}_prediction'],p>=.5)
        assert sum(r['confusion_matrix_tn_fp_fn_tp'])==len(pred)
    assert report['dummy']['precision'] is None


def test_bootstrap_draws_shared_and_interval_recoverable():
    pred=pd.read_csv(OUT/'test_predictions.csv');idx=np.load(OUT/'bootstrap_indices.npz')['indices']
    draws=pd.read_csv(OUT/'bootstrap_draws.csv');cis=read_json(OUT/'bootstrap_intervals.json')
    assert idx.shape==(2000,len(pred))
    for b in [0,17,1999]:
        for name in ['logistic_regression','dummy','random_forest']:
            r=binary_metrics(pred.y_true.to_numpy()[idx[b]],pred[f'{name}_probability'].to_numpy()[idx[b]])
            stored=draws[(draws.replicate==b)&(draws.model==name)].iloc[0]
            assert stored.brier==pytest.approx(r['brier'],abs=1e-12)
    for key in ['average_precision','roc_auc','brier']:
        values=draws[draws.model=='logistic_regression'][key].to_numpy()
        assert cis['logistic_regression'][key]['lower']==pytest.approx(np.quantile(values,.025))
        pair=read_json(OUT/'paired_differences.json')['random_forest'][key]
        differences=values-draws[draws.model=='random_forest'][key].to_numpy()
        assert pair['lower']==pytest.approx(np.quantile(differences,.025))
    assert cis['dummy']['precision']['valid_replicates']==0


def test_calibration_subgroup_and_importance_accounting():
    pred=pd.read_csv(OUT/'test_predictions.csv');cal=pd.read_csv(OUT/'lr_calibration_bins.csv')
    assert cal.n.sum()==len(pred) and cal.positive_n.sum()==pred.y_true.sum()
    sub=pd.read_csv(OUT/'subgroup_metrics.csv')
    for name in ['logistic_regression','dummy','random_forest']:
        for scheme in ['age_primary','age_detailed','income_primary']:
            g=sub[(sub.model==name)&(sub.scheme==scheme)]
            assert g.n.sum()==len(pred) and g.positive_n.sum()==pred.y_true.sum()
            assert (g.positive_n+g.negative_n==g.n).all()
    means=pd.read_csv(OUT/'validation_permutation_importance.csv').set_index('feature')
    raw=pd.read_csv(OUT/'validation_permutation_repeats.csv').drop(columns='repeat')
    assert len(raw)==30 and len(means)==8
    for c in raw:
        assert means.loc[c,'mean_ap_drop']==pytest.approx(raw[c].mean())
        assert means.loc[c,'sd_ap_drop']==pytest.approx(raw[c].std(ddof=0))
    assert sha256(ROOT/'models/cfpb/stage4_v1/stability.csv')==sha256(OUT/'stage4_development_stability.csv')
