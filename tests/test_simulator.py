"""Financial identities, boundary behavior, state isolation and standalone use."""
from copy import deepcopy
from dataclasses import FrozenInstanceError
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import pytest
from src.input_validation import validate_inputs, SimulationInputError, AMOUNT_FIELDS
from src.bnpl_simulator import calculate_monthly, compare_scenarios
from src.simulator_presentation import run_simulation

CASE={'I':4500,'E':2500,'D':700,'B0':400,'Bnew':200,'S':1000}


def test_supplied_example_all_scenarios_and_deltas():
    inputs,settings=validate_inputs(CASE,income_drop=.2,bnpl_reduction=200)
    scenes=compare_scenarios(inputs,settings)
    assert [r.metrics.cash_buffer.value for r in scenes]==[900,700,0,-200,1100]
    assert [r.deltas.cash_buffer.value for r in scenes]==[0,-200,-900,-1100,200]
    assert scenes[0].metrics.repayment_to_income.value==Fraction(1100,4500)
    assert scenes[0].metrics.savings_coverage.value==Fraction(1000,3600)
    assert scenes[1].metrics.total_bnpl.value==600
    assert scenes[2].effective_inputs.Bnew==0 and scenes[2].effective_inputs.I==3600
    assert scenes[3].effective_inputs.Bnew==200 and scenes[3].effective_inputs.I==3600
    assert scenes[4].effective_inputs.I==4500 and scenes[4].effective_inputs.B0==200


@pytest.mark.parametrize('field',AMOUNT_FIELDS)
@pytest.mark.parametrize('invalid',[-1,float('nan'),float('inf'),float('-inf'),True,'200',None,complex(1,2),[]])
def test_invalid_monetary_inputs_are_field_errors(field,invalid):
    payload={**CASE,field:invalid};r=run_simulation(payload)
    assert r['status']=='invalid_input' and not r['scenarios']
    assert any(e['field']==field for e in r['errors'])


def test_missing_unknown_fields_and_input_container():
    payload=dict(CASE);del payload['E'];payload['unknown']=3
    r=run_simulation(payload)
    assert {e['field'] for e in r['errors']}=={'E','unknown'}
    assert run_simulation([])['status']=='invalid_input'
    assert run_simulation(None)['status']=='invalid_input'


@pytest.mark.parametrize('currency',[None,1,'','AU','US dollars',' AUD','A1D'])
def test_currency_is_one_explicit_label(currency):
    assert run_simulation({**CASE,'currency':currency})['status']=='invalid_input'


def test_default_currency_and_no_implicit_conversion():
    a=run_simulation(CASE);b=run_simulation({**CASE,'currency':'usd'})
    assert a['currency']=='AUD' and b['currency']=='USD'
    assert a['scenarios'][0]['metrics']['cash_buffer']['value']==b['scenarios'][0]['metrics']['cash_buffer']['value']=='900'


@pytest.mark.parametrize('drop',[-.01,1.01,20,float('inf'),float('nan'),False,'0.2'])
def test_invalid_income_shock(drop):
    r=run_simulation(CASE,income_drop=drop)
    assert r['status']=='invalid_input' and any(e['field']=='income_drop' for e in r['errors'])


@pytest.mark.parametrize('reduction',[-1,401,float('inf'),float('nan'),True,'200'])
def test_invalid_bnpl_reduction(reduction):
    r=run_simulation(CASE,bnpl_reduction=reduction)
    assert r['status']=='invalid_input' and any(e['field']=='bnpl_reduction' for e in r['errors'])


def test_zero_income_preserves_cash_flow_with_explained_na():
    r=run_simulation({**CASE,'I':0})
    assert r['status']=='partial'
    current=r['scenarios'][0]
    assert current['metrics']['cash_buffer']['value']=='-3600'
    assert current['metrics']['repayment_to_income']['status']=='unavailable'
    assert current['metrics']['repayment_to_income']['reason']
    assert current['display']['repayment_to_income']['text']=='N/A'
    assert any(m['code']=='zero_income' for m in current['messages'])


def test_all_zero_and_zero_outflow_denominators():
    r=run_simulation(dict.fromkeys(AMOUNT_FIELDS,0),income_drop=1)
    assert r['status']=='partial'
    for scene in r['scenarios']:
        assert scene['metrics']['cash_buffer']['value']=='0'
        for key in ['repayment_to_income','savings_coverage']:
            assert scene['metrics'][key]['value'] is None and scene['metrics'][key]['reason']
    positive_income=run_simulation({**dict.fromkeys(AMOUNT_FIELDS,0),'I':100,'S':50})
    assert positive_income['scenarios'][0]['metrics']['repayment_to_income']['value']=='0'
    assert positive_income['scenarios'][0]['metrics']['savings_coverage']['value'] is None


def test_extreme_shocks_and_complete_existing_bnpl_reduction():
    r=run_simulation(CASE,income_drop=1,bnpl_reduction=400)
    assert r['scenarios'][2]['effective_inputs']['I']=='0'
    assert r['scenarios'][2]['metrics']['cash_buffer']['value']=='-3600'
    assert r['scenarios'][3]['metrics']['cash_buffer']['value']=='-3800'
    assert r['scenarios'][4]['effective_inputs']['B0']=='0'
    zero=run_simulation(CASE,income_drop=0,bnpl_reduction=0)
    assert zero['scenarios'][2]['metrics']==zero['scenarios'][0]['metrics']
    assert zero['scenarios'][4]['metrics']==zero['scenarios'][0]['metrics']


def test_deltas_never_invent_changes_when_metric_is_unavailable():
    r=run_simulation(CASE,income_drop=1)
    m=r['scenarios'][2]['delta_from_current']['repayment_to_income']
    assert m['value'] is None and m['reason']
    r=run_simulation({**dict.fromkeys(AMOUNT_FIELDS,0),'I':100,'Bnew':10})
    m=r['scenarios'][1]['delta_from_current']['savings_coverage']
    assert m['value'] is None and 'current-case' in m['reason']


def test_repeatability_and_no_input_or_between_scenario_mutation():
    payload=deepcopy(CASE);before=deepcopy(payload)
    a=run_simulation(payload,income_drop=.2,bnpl_reduction=200)
    assert payload==before and a==run_simulation(payload,income_drop=.2,bnpl_reduction=200)
    a['scenarios'][1]['effective_inputs']['I']='corrupted display copy'
    assert a['scenarios'][0]['effective_inputs']['I']=='4500'
    assert payload==before
    i,s=validate_inputs(payload)
    with pytest.raises(FrozenInstanceError):i.I=Fraction(0)


def test_exact_decimal_money_and_large_finite_values():
    payload={'I':.3,'E':.1,'D':.1,'B0':.1,'Bnew':0,'S':Decimal('.1')}
    i,s=validate_inputs(payload)
    assert calculate_monthly(i).cash_buffer.value==0
    for payload in [dict.fromkeys(AMOUNT_FIELDS,sys.float_info.max),{**CASE,'I':5e-324,'D':sys.float_info.max}]:
        r=run_simulation(payload,income_drop=1)
        assert r['status'] in ['ok','partial']
        encoded=json.dumps(r,allow_nan=False)
        assert 'Infinity' not in encoded and 'NaN' not in encoded
        for scene in r['scenarios']:
            for m in scene['metrics'].values():
                assert m['value'] is None or Decimal(m['value']).is_finite()


def test_monotonicity_and_finite_results_across_many_legal_cases():
    rng=random.Random(5557)
    for _ in range(200):
        values={key:Decimal(rng.randrange(0,100000))/100 for key in AMOUNT_FIELDS}
        i,s=validate_inputs(values,income_drop=Fraction(rng.randrange(101),100),bnpl_reduction=values['B0']/2)
        scenes=compare_scenarios(i,s)
        assert scenes[1].metrics.cash_buffer.value<=scenes[0].metrics.cash_buffer.value
        assert scenes[1].metrics.cash_buffer.value==scenes[0].metrics.cash_buffer.value-i.Bnew
        assert scenes[3].metrics.cash_buffer.value<=scenes[2].metrics.cash_buffer.value
        assert scenes[4].metrics.cash_buffer.value>=scenes[0].metrics.cash_buffer.value
        r=run_simulation(values,income_drop=Fraction(1,5),bnpl_reduction=values['B0']/2)
        json.dumps(r,allow_nan=False)


def test_calculator_runs_without_site_packages_or_models():
    root=Path(__file__).resolve().parents[1]
    code=f"import sys; sys.path.insert(0,{str(root)!r}); from src.simulator_presentation import run_simulation; r=run_simulation({CASE!r}); assert r['status']=='ok'; assert not any(x in sys.modules for x in ['sklearn','pandas','numpy','joblib']); print('standalone')"
    result=subprocess.run([sys.executable,'-I','-S','-c',code],capture_output=True,text=True,check=True)
    assert result.stdout.strip()=='standalone'


def test_assumptions_and_hypothetical_notice_are_attached():
    r=run_simulation(CASE,income_drop=.2,bnpl_reduction=200)
    assert r['calculation_type']=='deterministic_monthly_financial_calculation'
    for scene in r['scenarios']:
        assert any('E excludes' in s for s in scene['assumptions'])
        assert any('due date' in s for s in scene['assumptions'])
        assert len(scene['effective_inputs'])==7
        assert len(scene['delta_from_current'])==6
    assert any('contractual' in m['message'] for m in r['scenarios'][-1]['messages'])
    assert any(m['code']=='negative_cash_flow' for m in r['scenarios'][3]['messages'])


def test_ratio_changes_display_percentage_points_not_relative_percent():
    r=run_simulation(CASE,income_drop=.2,bnpl_reduction=200)
    added=r['scenarios'][1]
    assert added['display']['repayment_to_income']['text']=='28.89%'
    assert added['delta_display']['repayment_to_income']['text']=='4.44 percentage points'
