"""Behavioral checks for mapping, leakage boundaries and persisted inference."""
import json
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier
from src.common import ROOT, read_json, sha256
from src.preprocessing import map_target, clean_features, build_pipeline

@pytest.fixture
def raw():
    return pd.read_csv(ROOT/'data/raw/cfpb/NFWBS_PUF_2016_data.csv').set_index('PUF_ID',drop=False)

@pytest.fixture
def artifact():
    return joblib.load(ROOT/'models/cfpb/stage3_v2/logistic_regression.joblib')

def test_labels_exclude_missing_and_refuse_unknown():
    result=map_target(pd.Series([1,2,3,-1,np.nan]))
    assert result.iloc[:3].tolist()==[0,1,1]
    assert result.iloc[3:].isna().all()
    with pytest.raises(ValueError): map_target(pd.Series([0]))

def test_special_codes_and_privacy_collapse(raw):
    frame=raw.head(5).copy()
    frame['SAVINGSRANGES']=[1,7,98,99,-1]
    frame['EMPLOY']=[4,5,6,8,99]
    result=clean_features(frame)
    assert result.SAVINGSRANGES.iloc[:2].tolist()==[1,7]
    assert result.SAVINGSRANGES.iloc[2:].isna().all()
    assert result.EMPLOY.iloc[:4].tolist()==[4,4,4,4]
    assert pd.isna(result.EMPLOY.iloc[4])

def test_invalid_and_absent_columns_rejected(raw,artifact):
    frame=raw.head(2).copy()
    frame['SAVINGSRANGES']=4500
    with pytest.raises(ValueError): artifact.predict_proba(frame)
    with pytest.raises(ValueError): artifact.predict_proba(raw.head(2).drop(columns='HOUSING'))

def test_locked_splits_cover_eligible_ids_only(raw):
    split=read_json('data/splits/cfpb_split_ids.json')
    groups=[set(split[s]) for s in ['train','validation','test']]
    assert [len(g) for g in groups]==[3810,1270,1270]
    assert not (groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
    # Membership/eligibility only; never calculates test metrics or predictions.
    assert set.union(*groups)==set(raw.index[map_target(raw.ENDSMEET).notna()])
    assert split['data_sha256']==sha256(ROOT/'data/raw/cfpb/NFWBS_PUF_2016_data.csv')

def test_imputation_fit_on_training_only(raw,artifact):
    split=read_json('data/splits/cfpb_split_ids.json')
    x=clean_features(raw.loc[split['train']])
    expected=np.array([x[c].mode().min() for c in x])
    fitted=artifact['preprocessor'].named_transformers_['categorical']['imputer'].statistics_
    np.testing.assert_array_equal(fitted,expected)
    assert list(artifact['codebook'].schema)==list(read_json('config/feature_schema.json')['features'])
    assert 'ENDSMEET' not in artifact['codebook'].schema
    assert 'finalwt' not in artifact['codebook'].schema

def test_roundtrip_validation_probabilities(raw,artifact):
    split=read_json('data/splits/cfpb_split_ids.json')
    p=artifact.predict_proba(raw.loc[split['validation']])[:,1]
    saved=pd.read_csv(ROOT/'models/cfpb/stage3_v2/validation_predictions.csv')
    np.testing.assert_array_equal(saved.PUF_ID,split['validation'])
    np.testing.assert_allclose(p,saved.logistic_regression,atol=1e-14)
    assert np.isfinite(p).all() and ((p>=0)&(p<=1)).all()

def test_pipeline_handles_missing_values_and_unseen_valid_codes(raw):
    frame=raw.head(6).copy()
    frame['HOUSING']=1
    a=build_pipeline(DummyClassifier(strategy='prior'))
    b=build_pipeline(DummyClassifier(strategy='prior'))
    assert a['preprocessor'] is not b['preprocessor']
    a.fit(frame,pd.Series([0,1,0,1,0,1]))
    probe=frame.head(1).copy(); probe['HOUSING']=3; probe['SAVINGSRANGES']=np.nan
    assert np.isfinite(a.predict_proba(probe)).all()

def test_metrics_independent_recalculation():
    saved=pd.read_csv(ROOT/'models/cfpb/stage3_v2/validation_predictions.csv')
    report=read_json('models/cfpb/stage3_v2/validation_metrics.json')
    y=saved.y_true.to_numpy()
    for name in ['dummy','logistic_regression']:
        p=saved[name].to_numpy(); m=report[name]['validation']
        assert np.mean((p-y)**2)==pytest.approx(m['brier'])
        # Pairwise probability-of-correct-ranking definition of AUC.
        comparisons=p[y==1][:,None]-p[y==0][None,:]
        auc=np.mean((comparisons>0)+0.5*(comparisons==0))
        assert auc==pytest.approx(m['roc_auc'])
        assert np.mean((p>=.5)==y)==pytest.approx(m['accuracy'])
        # Integrate precision over recall increments at distinct score thresholds (AP).
        order=np.argsort(-p,kind='stable')
        ys=y[order]; ps=p[order]
        ends=np.r_[np.flatnonzero(np.diff(ps)),len(ps)-1]
        tp=np.cumsum(ys)[ends]
        ap=np.sum((np.diff(np.r_[0,tp])/y.sum())*(tp/(ends+1)))
        assert ap==pytest.approx(m['average_precision'])
    assert report['dummy']['validation']['average_precision']==pytest.approx(y.mean())

def test_artifact_integrity_and_test_not_evaluated():
    manifest=read_json('models/cfpb/stage3_v2/run_manifest.json')
    assert manifest['test_evaluated'] is False
    for name,digest in manifest['artifacts_sha256'].items():
        assert sha256(ROOT/'models/cfpb/stage3_v2'/name)==digest
    # Historical development directories must remain free of test predictions.
    for directory in ['models/cfpb/stage3_v2', 'models/cfpb/stage4_v1']:
        assert not list((ROOT/directory).rglob('*test*prediction*'))
