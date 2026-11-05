"""Local application acceptance: real interfaces, session isolation and graceful failures."""
from copy import deepcopy
from threading import RLock
import json
import tomllib
import joblib
import numpy as np
import pytest
from scipy.special import expit
from sklearn.pipeline import Pipeline
from streamlit.testing.v1 import AppTest
from src.common import ROOT,read_json,sha256
from src import app_services as services
from src.app_inputs import FIELDS,MISSING,screen_options,screen_payload


def app():
    result=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    assert not result.exception
    return result


def load_screen(at):
    at.button(key='screen_example').click().run();at.button(key='run_screen').click().run()
    assert not at.exception
    return at.session_state['screen_submission']['result']


def load_stress(at):
    at.radio(key='workspace').set_value('Stress').run();at.button(key='stress_example').click().run();at.button(key='run_stress').click().run()
    assert not at.exception
    return at.session_state['stress_submission']['result']['simulation']


def test_initial_empty_state_and_schema_mapping_do_not_load_model(monkeypatch):
    def forbidden(*a,**k):pytest.fail('Initial view must not score or load an explainer')
    monkeypatch.setattr(services,'get_predictor',forbidden);monkeypatch.setattr(services,'get_explainer',forbidden)
    at=app();assert len(at.selectbox)==8 and len(at.metric)==0
    assert all(w.value is None for w in at.selectbox)
    for field,meta in FIELDS.items():
        options=screen_options(field)
        assert all(options[str(k)]==v for k,v in meta['labels'].items())
        assert MISSING in options
    with pytest.raises(ValueError):screen_payload(dict.fromkeys(FIELDS,None))
    assert all(v is None for v in screen_payload(dict.fromkeys(FIELDS,MISSING)).values())


def test_web_prediction_shap_and_template_match_direct_frozen_pipeline(monkeypatch):
    monkeypatch.setattr(Pipeline,'fit',lambda *a,**k:pytest.fail('UI cannot fit'))
    at=app();result=load_screen(at);codes=screen_payload(at.session_state['screen_draft'])
    model=joblib.load(ROOT/read_json('config/stage5_frozen.json')['artifact'])
    import pandas as pd
    p=model.predict_proba(pd.DataFrame([codes],columns=list(FIELDS)).astype(float))[0,1]
    assert model.classes_.tolist()==[0,1] and result['prediction']['probability']==p
    assert result['prediction']['threshold']==.5 and result['prediction']['classification']==int(p>=.5)
    local=result['local'];assert local['probability']==p
    assert local['base_value_log_odds']+sum(r['contribution_log_odds'] for r in local['contributions'])==pytest.approx(local['decision_function'],abs=1e-10)
    assert expit(local['decision_function'])==pytest.approx(p,abs=1e-12)
    assert result['template']['llm_status']=='disabled'
    assert any(m.value==f'{p:.2%}' for m in at.metric)
    text=' '.join(m.value for m in at.markdown)
    assert 'Contributions to this model estimate' in text and r'\$0' in text


def test_changed_inputs_reset_navigation_and_separate_sessions():
    at=app();load_screen(at)
    at.selectbox(key='screen_widget_HOUSING').set_value('2').run()
    assert 'screen_submission' not in at.session_state and not at.metric
    at.radio(key='workspace').set_value('Explain').run()
    assert any('Submit Screen first' in i.value for i in at.info)
    at.radio(key='workspace').set_value('Screen').run()
    assert at.selectbox(key='screen_widget_HOUSING').value=='2'
    at.button(key='run_screen').click().run()
    assert at.session_state['screen_submission']['inputs']['HOUSING']=='2'
    at.radio(key='workspace').set_value('Stress').run();at.radio(key='workspace').set_value('Screen').run()
    assert at.metric and at.selectbox(key='screen_widget_HOUSING').value=='2'
    other=app();assert not other.metric and all(w.value is None for w in other.selectbox)
    at.button(key='screen_reset').click().run()
    assert 'screen_submission' not in at.session_state and not at.metric and all(w.value is None for w in at.selectbox)


def test_simulator_example_ui_values_ratios_and_template_unchanged():
    at=app();sim=load_stress(at)
    assert sim==read_json('data/metadata/extensions_baseline.json')['simulator']
    assert [s['metrics']['cash_buffer']['value'] for s in sim['scenarios']]==['900','700','0','-200','1100']
    at.selectbox(key='stress_inspect').select('Added BNPL + income shock').run()
    scenario=sim['scenarios'][3]
    assert [(m.value,m.delta) for m in at.metric]==[(scenario['display'][k]['text'],scenario['delta_display'][k]['text']) for k in ['cash_buffer','repayment_to_income','savings_coverage']]
    assert 'percentage points' in at.metric[1].delta
    assert any('expenses and repayments exceed income' in m.value for m in at.markdown)
    at.number_input(key='stress_widget_Bnew').set_value(250.).run()
    assert 'stress_submission' not in at.session_state and not at.metric

@pytest.mark.parametrize('expenses',[0.,100.])
def test_zero_income_zero_denominator_and_negative_buffer_ui(expenses):
    at=app();at.radio(key='workspace').set_value('Stress').run()
    for field in ['I','E','D','B0','Bnew','S']:at.number_input(key='stress_widget_'+field).set_value(expenses if field=='E' else 0.)
    at.run();at.button(key='run_stress').click().run()
    assert not at.exception
    sim=at.session_state['stress_submission']['result']['simulation']
    assert sim['status']=='partial' and at.metric[1].value=='N/A'
    assert not any('NaN' in str(m.value) or 'Infinity' in str(m.value) for m in at.metric)
    if expenses:assert at.metric[0].value=='AUD -100.00'
    else:assert at.metric[2].value=='N/A'


def test_invalid_reduction_and_invalid_values_are_rejected():
    at=app();load_stress(at);at.number_input(key='stress_widget_bnpl_reduction').set_value(450.).run();at.button(key='run_stress').click().run()
    assert not at.exception and 'stress_submission' not in at.session_state
    assert at.warning and not at.metric
    baseline={'I':4500,'E':2500,'D':700,'B0':400,'Bnew':200,'S':1000}
    for value in [-1,float('nan'),float('inf'),'invalid']:
        bad=baseline.copy();bad['I']=value
        assert services.stress(bad,income_drop_percent=20,bnpl_reduction=0)['simulation']['status']=='invalid_input'


def test_shap_missing_keeps_valid_prediction_and_simulation(monkeypatch):
    def missing():raise FileNotFoundError('mock missing background')
    monkeypatch.setattr(services,'get_explainer',missing)
    at=app();result=load_screen(at)
    assert result['status']=='partial' and result['local'] is None and result['template'] is None
    assert len(at.metric)==1 and any('temporarily unavailable' in w.value for w in at.warning)
    assert load_stress(at)['status']=='ok'


def test_wrong_local_probability_is_withheld(monkeypatch):
    class Wrong:
        def explain(self,codes):return {'probability':0.01,'artifact_sha256':'wrong'}
    monkeypatch.setattr(services,'get_explainer',lambda:(Wrong(),RLock()))
    at=app();result=load_screen(at)
    assert result['status']=='partial' and result['local'] is None and at.metric[0].value=='83.85%'


def test_missing_model_does_not_block_stress(monkeypatch):
    def missing():raise FileNotFoundError('mock missing model')
    monkeypatch.setattr(services,'get_predictor',missing)
    at=app();at.button(key='screen_example').click().run();at.button(key='run_screen').click().run()
    assert not at.exception and not at.metric and 'screen_submission' not in at.session_state
    assert any('model is unavailable' in w.value for w in at.warning)
    assert load_stress(at)['scenarios'][0]['display']['cash_buffer']['text']=='AUD 900.00'


def test_saved_model_evidence_and_missing_artifact_state(monkeypatch):
    at=app();at.radio(key='workspace').set_value('Model').run()
    assert not at.exception
    saved=read_json('outputs/evaluation/stage5_v1/test_metrics.json')['logistic_regression']
    assert [m.value for m in at.metric]==[f'{saved[k]:.4f}' for k in ['average_precision','roc_auc','brier']]
    actual=services.evidence
    def without_metrics(relative):
        if str(relative).endswith('/test_metrics.json'):return {'status':'unavailable','path':str(relative),'message':'Saved test metrics unavailable; no placeholder.'}
        return actual(relative)
    monkeypatch.setattr(services,'evidence',without_metrics)
    at.run();assert not at.exception and not at.metric
    assert any('no placeholder' in w.value for w in at.warning)


def test_no_training_bootstrap_background_generation_or_external_api(monkeypatch):
    import requests,urllib.request
    import src.cfpb_local_explanation as local
    import src.evaluation_stats as stats
    from src.llm_adapter import OptionalLLMAdapter
    def forbidden(*a,**k):pytest.fail('App must not train, bootstrap, generate background or call external APIs')
    for owner,name in [(Pipeline,'fit'),(stats,'paired_bootstrap'),(local,'prepare_background'),(OptionalLLMAdapter,'rewrite'),(requests.sessions.Session,'request'),(urllib.request,'urlopen')]:monkeypatch.setattr(owner,name,forbidden)
    at=app();load_screen(at);load_stress(at)
    at.radio(key='workspace').set_value('Explain').run();assert not at.exception
    at.radio(key='workspace').set_value('Model').run();assert not at.exception
    config=tomllib.loads((ROOT/'.streamlit/config.toml').read_text())
    assert config['browser']['gatherUsageStats'] is False and config['server']['address']=='127.0.0.1'
    assert config['server']['enableCORS'] and config['server']['enableXsrfProtection']


@pytest.fixture(scope='module',autouse=True)
def preserved_runtime_files():
    files=[]
    for directory in ['src','config','models']:
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    return {str(p.relative_to(ROOT)):sha256(p) for p in files}


def test_original_files_still_unchanged_after_ui_runs(preserved_runtime_files):
    for name,h in preserved_runtime_files.items():assert sha256(ROOT/name)==h,name


def test_feedback_input_order_and_visible_scenario_summaries():
    at=app();sim=load_stress(at)
    assert [w.key for w in at.number_input][:6]==['stress_widget_'+k for k in ['I','E','D','B0','Bnew','S']]
    assert all('Monthly' in w.label for w in list(at.number_input)[:5])
    assert 'current available balance' in at.number_input(key='stress_widget_S').label
    text='\n'.join(m.value for m in at.markdown)
    assert 'Savings are not included in monthly income or the monthly cash buffer' in text
    for s in sim['scenarios']:
        assert '**'+s['title']+'**' in text
        assert 'Final monthly cash buffer: '+s['display']['cash_buffer']['text'] in text
        assert 'Change from current: '+s['delta_display']['cash_buffer']['text'] in text
    assert text.count('Status: Surplus')==3
    assert text.count('Status: Shortfall')==1 and text.count('Status: Break-even')==1
    assert 'income reduction 20%' in text
    at.number_input(key='stress_widget_S').set_value(2000.).run()
    assert 'stress_submission' not in at.session_state
    assert not any('Final monthly cash buffer:' in m.value for m in at.markdown)
    at.button(key='run_stress').click().run()
    updated=at.session_state['stress_submission']['result']['simulation']
    assert [s['metrics']['cash_buffer'] for s in updated['scenarios']]==[s['metrics']['cash_buffer'] for s in sim['scenarios']]
    assert float(updated['scenarios'][0]['metrics']['savings_coverage']['value'])==pytest.approx(2*float(sim['scenarios'][0]['metrics']['savings_coverage']['value']))
    at.button(key='stress_reset').click().run()
    assert 'stress_submission' not in at.session_state and all(w.value is None for w in list(at.number_input)[:6])
    assert not any('Final monthly cash buffer:' in m.value for m in at.markdown)


def test_purchase_plan_switch_invalidation_and_example():
    at=app(); original=load_stress(at)
    at.radio(key='plan_mode').set_value('Estimate from a purchase plan').run()
    assert 'stress_submission' not in at.session_state
    at.number_input(key='plan_purchase').set_value(600.).run()
    at.button(key='apply_plan').click().run()
    assert at.session_state['stress_draft']['Bnew']==200
    at.button(key='run_stress').click().run()
    assert at.session_state['stress_submission']['result']['simulation']==original
    at.number_input(key='plan_purchase').set_value(100.).run()
    assert 'stress_submission' not in at.session_state and at.session_state['stress_draft']['Bnew'] is None
    at.button(key='apply_plan').click().run()
    assert at.session_state['stress_draft']['Bnew']==33.34
    at.button(key='apply_plan').click().run()
    assert at.session_state['stress_draft']['Bnew']==33.34
    at.radio(key='plan_mode').set_value('Enter monthly repayment directly').run()
    assert at.session_state['stress_draft']['Bnew']==200
    at.button(key='stress_reset').click().run()
    assert at.radio(key='plan_mode').value=='Enter monthly repayment directly'
    at.button(key='stress_example').click().run()
    assert at.session_state['stress_draft']['Bnew']==200
