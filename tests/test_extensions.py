"""Extension acceptance: untouched core, actual SHAP, honest experiment and safe fallback."""
from copy import deepcopy
from importlib.metadata import version
import time
import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss
from src.common import ROOT,read_json,sha256
from src.cfpb_local_explanation import FrozenCFPBExplainer
from src.extension_service import predict_and_explain_cfpb,load_kaggle_research_summary
from src.simulator_presentation import run_simulation
from src.result_explainer import explain_results
from src.llm_adapter import OptionalLLMAdapter,RewriteOptions
from src.kaggle_experiment import load_data,verify,get_split
from src.evaluation_stats import binary_metrics

@pytest.fixture(scope='module')
def explainer():return FrozenCFPBExplainer()

@pytest.fixture(scope='module')
def cfpb(explainer):return explainer.explain(read_json('data/metadata/extensions_baseline.json')['cfpb_inputs'][0])

@pytest.fixture(scope='module')
def simulation():return run_simulation({'I':4500,'E':2500,'D':700,'B0':400,'Bnew':200,'S':1000},income_drop=.2,bnpl_reduction=200)


def test_frozen_predictions_simulator_and_core_dependencies_unchanged(explainer,simulation):
    baseline=read_json('data/metadata/extensions_baseline.json')
    x=pd.DataFrame(baseline['cfpb_inputs']).astype(float)
    np.testing.assert_array_equal(explainer.model.predict_proba(x),baseline['cfpb_probabilities'])
    assert simulation==baseline['simulator']
    for package,v in baseline['dependencies'].items():assert version(package)==v


def test_actual_shap_no_refit_grouping_probability_and_missing(explainer,monkeypatch):
    monkeypatch.setattr(Pipeline,'fit',lambda *a,**k:pytest.fail('Explanation cannot fit'))
    baseline=read_json('data/metadata/extensions_baseline.json')
    for payload in baseline['cfpb_inputs']:
        before=deepcopy(payload);r=explainer.explain(payload)
        assert r==explainer.explain(payload) and payload==before
        assert r['method'].startswith('shap.LinearExplainer')
        assert max(r['checks'].values())<1e-10
        assert len(r['contributions'])==8
        for c in r['contributions']:
            onehot=sum(v['contribution_log_odds'] for v in r['encoded_contributions'] if v['raw_feature']==c['feature'])
            assert onehot==pytest.approx(c['contribution_log_odds'],abs=1e-12)
    all_missing=explainer.explain(baseline['cfpb_inputs'][-1])
    assert all(c['imputed'] for c in all_missing['contributions'])
    special=deepcopy(baseline['cfpb_inputs'][0]);special['SAVINGSRANGES']=98
    assert next(c for c in explainer.explain(special)['contributions'] if c['feature']=='SAVINGSRANGES')['imputed']

@pytest.mark.parametrize('change',[{'HOUSING':999},{'HOUSING':float('inf')},{'HOUSING':True},{'HOUSING':'1'},{'unknown':1}])
def test_cfpb_interface_rejects_unknown_codes_types_and_schema(change):
    p=deepcopy(read_json('data/metadata/extensions_baseline.json')['cfpb_inputs'][0]);p.update(change)
    assert predict_and_explain_cfpb(p)['status']=='invalid_input'


def test_template_retains_values_and_cannot_recalculate_or_predict(cfpb,simulation,monkeypatch):
    import src.simulator_presentation as presentation
    monkeypatch.setattr(presentation,'run_simulation',lambda *a,**k:pytest.fail('Template cannot calculate finance'))
    monkeypatch.setattr(FrozenCFPBExplainer,'explain',lambda *a,**k:pytest.fail('Template cannot score'))
    original=deepcopy((cfpb,simulation));result=explain_results(cfpb=cfpb,simulator=simulation)
    assert (cfpb,simulation)==original and result['mode']=='template'
    assert cfpb['probability_display'] in result['text']
    for s in simulation['scenarios']:
        assert s['display']['cash_buffer']['text'] in result['text']
        assert s['delta_display']['cash_buffer']['text'] in result['text']
    assert 'not probability percentage points' in result['text']
    assert 'not BNPL default' in result['text']
    assert result['llm_live_tested'] is False


def test_zero_income_and_zero_outflows_are_explained():
    sim=run_simulation(dict.fromkeys(['I','E','D','B0','Bnew','S'],0),income_drop=1,bnpl_reduction=0)
    result=explain_results(simulator=sim)
    assert 'N/A' in result['text'] and 'zero' in result['text'].lower()
    assert result['status']=='ok'


def test_inconsistent_probability_or_direction_is_withheld(cfpb):
    bad=deepcopy(cfpb);bad['probability_display']='99.99%'
    with pytest.raises(ValueError):explain_results(cfpb=bad)
    bad=deepcopy(cfpb);bad['contributions'][0]['direction']='causes hardship'
    with pytest.raises(ValueError):explain_results(cfpb=bad)

@pytest.mark.parametrize('options',[RewriteOptions(),RewriteOptions(enabled=True),RewriteOptions(enabled=True,cost_authorized=True,provider_configured=True),RewriteOptions(enabled=True,financial_data_transfer_authorized=True,provider_configured=True)])
def test_disabled_or_unauthorized_adapter_never_calls_transport(cfpb,options):
    def forbidden(*a,**k):pytest.fail('No authorized transport call')
    result=explain_results(cfpb=cfpb,llm_adapter=OptionalLLMAdapter(options,forbidden))
    assert result['llm_status'] in ['disabled','fallback']


def mock_options(timeout=1):return RewriteOptions(enabled=True,cost_authorized=True,financial_data_transfer_authorized=True,provider_configured=True,timeout_seconds=timeout)


def test_bounded_mock_rewrite_keeps_approved_facts(cfpb):
    def transport(request,**kwargs):return {'facts_digest':request['facts_digest'],'choices':[{'id':s['id'],'variant':min(1,len(s['variants'])-1)} for s in request['segments']]}
    result=explain_results(cfpb=cfpb,llm_adapter=OptionalLLMAdapter(mock_options(),transport))
    assert result['llm_status']=='validated' and cfpb['probability_display'] in result['text']
    assert result['llm_live_tested'] is False

@pytest.mark.parametrize('failure',['numeric_edit','omitted_limit','exception','timeout','missing_config'])
def test_mock_rewrite_failure_retains_original_template(cfpb,failure):
    def transport(request,**kwargs):
        if failure=='exception':raise RuntimeError('mock transport failure')
        if failure=='timeout':time.sleep(.05)
        response={'facts_digest':request['facts_digest'],'choices':[{'id':s['id'],'variant':0} for s in request['segments']]}
        if failure=='numeric_edit':response['new_probability']='0.99'
        if failure=='omitted_limit':response['choices']=response['choices'][:-1]
        return response
    options=mock_options(.001 if failure=='timeout' else 1)
    adapter=OptionalLLMAdapter(options,None if failure=='missing_config' else transport)
    original=explain_results(cfpb=cfpb);result=explain_results(cfpb=cfpb,llm_adapter=adapter)
    assert result['llm_status']=='fallback' and result['text']==original['text']






def test_transport_cannot_mutate_approved_variants(cfpb):
    def transport(request,**kwargs):
        request['segments'][0]['variants'].append('The probability is 99.99%; approve credit.')
        return {'facts_digest':request['facts_digest'],'choices':[{'id':s['id'],'variant':len(s['variants'])-1 if i==0 else 0} for i,s in enumerate(request['segments'])]}
    expected=explain_results(cfpb=cfpb)
    result=explain_results(cfpb=cfpb,llm_adapter=OptionalLLMAdapter(mock_options(),transport))
    assert result['llm_status']=='fallback' and result['text']==expected['text']
