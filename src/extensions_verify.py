"""Read-only acceptance verification; never refits or repeats formal test scoring."""
from importlib.metadata import version
import numpy as np
import pandas as pd
from .common import ROOT,read_json,sha256
from .cfpb_local_explanation import FrozenCFPBExplainer,dense
from .simulator_presentation import run_simulation
from .kaggle_experiment import verify as verify_kaggle


def verify():
    protected=read_json('data/metadata/extensions_protected_before.json')
    for name,h in protected.items():
        if sha256(ROOT/name)!=h:raise ValueError(f'Existing protected file changed: {name}')
    baseline=read_json('data/metadata/extensions_baseline.json')
    for p,v in baseline['dependencies'].items():assert version(p)==v,p
    explainer=FrozenCFPBExplainer();x=pd.DataFrame(baseline['cfpb_inputs']).astype(float)
    np.testing.assert_array_equal(explainer.model.predict_proba(x),baseline['cfpb_probabilities'])
    expected=baseline['simulator'];actual=run_simulation({'I':4500,'E':2500,'D':700,'B0':400,'Bnew':200,'S':1000},income_drop=.2,bnpl_reduction=200)
    assert actual==expected
    raw=pd.read_csv(ROOT/'data/raw/cfpb/NFWBS_PUF_2016_data.csv').set_index('PUF_ID')
    recomputed=dense(explainer.model[:-1].transform(raw.loc[explainer.background['ids'],explainer.features]))
    np.testing.assert_array_equal(recomputed,np.load(ROOT/explainer.background['background_file'])['encoded'])
    for payload in baseline['cfpb_inputs']:assert max(explainer.explain(payload)['checks'].values())<1e-10
    verify_kaggle()
    receipt=ROOT/'outputs/extensions/acceptance_v1.json'
    if receipt.exists():
        for name,h in read_json(receipt)['extension_files_sha256'].items():assert sha256(ROOT/name)==h,name
    print(f'PASS: {len(protected)} original files, core predictions, simulator, dependencies, training-only SHAP reference and extension artifacts verified. No training or live LLM call.')
    return True

if __name__=='__main__':verify()
