"""Offline English explanations from trusted producer outputs; no finance arithmetic."""
from copy import deepcopy
import hashlib
import json
from decimal import Decimal
from .common import read_json

CFPB_LIMIT='This describes a contemporaneous survey-model estimate, not BNPL default, a personal cause, a causal action effect or an Australian credit decision. Local calibration overestimation and subgroup differences remain documented.'
SIM_LIMIT='Coverage assumes no new income and unchanged listed outflows. A positive monthly buffer does not guarantee cash on each due date. Reducing existing BNPL is hypothetical, not a contract change.'


def _validate_cfpb(result):
    freeze=read_json('config/stage5_frozen.json')
    if result.get('status')!='ok' or result.get('kind')!='cfpb_frozen_lr_local_explanation' or result.get('additivity_verified') is not True:raise ValueError('A verified frozen-model explanation is required')
    if result.get('artifact_sha256')!=freeze['artifact_sha256'] or result.get('threshold')!=freeze['threshold']:raise ValueError('Frozen-model contract mismatch')
    p=result.get('probability')
    if not isinstance(p,(int,float)) or not 0<=p<=1 or result.get('probability_display')!=f'{p:.2%}':raise ValueError('Invalid or inconsistent probability display')
    if result.get('classification')!=int(p>=freeze['threshold']):raise ValueError('Classification inconsistent with producer threshold')
    rows=result.get('contributions',[])
    if len(rows)!=8 or {r['feature'] for r in rows}!=set(freeze['features']):raise ValueError('Eight verified raw-input contributions required')
    for r in rows:
        v=r['contribution_log_odds']
        if not isinstance(v,(int,float)) or not Decimal(str(v)).is_finite() or r['contribution_display']!=f'{v:+.4f} log-odds':raise ValueError('Invalid contribution display')
        if r['direction']!=('increase' if v>0 else 'decrease' if v<0 else 'neutral'):raise ValueError('Inconsistent contribution direction')
    checks=result.get('checks',{})
    if set(checks)!={'encoded_additivity_absolute','raw_group_additivity_absolute','grouping_absolute','probability_absolute'} or any(not isinstance(v,(int,float)) or not 0<=v<=1e-10 for v in checks.values()):raise ValueError('Missing or failed reconstruction checks')


def _validate_simulator(result):
    if result.get('status') not in ['ok','partial'] or result.get('calculation_type')!='deterministic_monthly_financial_calculation':raise ValueError('Valid/partial simulator producer output required')
    keys=[s['key'] for s in result['scenarios']]
    if keys!=['current','added_bnpl','income_shock','added_bnpl_income_shock','reduced_existing_bnpl']:raise ValueError('Unexpected or missing independent scenarios')
    for s in result['scenarios']:
        for group,display_group in [('metrics','display'),('delta_from_current','delta_display')]:
            for name,m in s[group].items():
                if m['status']=='unavailable':
                    if m['value'] is not None or not m['reason'] or s[display_group][name]['text']!='N/A':raise ValueError('Missing ratio reason or inconsistent N/A')
                elif m['status']=='ok':
                    if not isinstance(m['value'],str) or not Decimal(m['value']).is_finite():raise ValueError('Nonfinite simulator metric')
                else:raise ValueError('Unknown metric status')
        if not s.get('assumptions'):raise ValueError('Scenario assumptions required')


def explanation_segments(*,cfpb=None,simulator=None):
    """Build factual segments; values/ratios/deltas remain producer-computed text."""
    segments=[]
    if cfpb is not None:
        _validate_cfpb(cfpb)
        summary=f'The frozen CFPB model estimates {cfpb["probability_display"]} for {cfpb["label_meaning"]} {cfpb["classification_text"]}; the fixed threshold is {cfpb["threshold_display"]}.'
        alternate=f'For the stated survey label, the frozen CFPB estimate is {cfpb["probability_display"]}. {cfpb["label_meaning"]} {cfpb["classification_text"]}; the fixed threshold is {cfpb["threshold_display"]}.'
        segments.append({'id':'cfpb_estimate','variants':[summary,alternate]})
        rows=sorted(cfpb['contributions'],key=lambda r:abs(r['contribution_log_odds']),reverse=True)[:3]
        parts=[f'{r["feature"]} ({r["raw_label"]}): {r["contribution_display"]}, direction {r["direction"]}' for r in rows]
        segments.append({'id':'cfpb_contributions','variants':['Contributions to this model estimate, relative to the fixed training background: '+'; '.join(parts)+'. These are log-odds contributions, not probability percentage points.']})
        segments.append({'id':'cfpb_limits','variants':[CFPB_LIMIT]})
    if simulator is not None:
        _validate_simulator(simulator)
        common_assumptions=[a for a in simulator['scenarios'][0]['assumptions'] if all(a in s['assumptions'] for s in simulator['scenarios'])]
        for s in simulator['scenarios']:
            d=s['display'];delta=s['delta_display']
            parts=[f'{s["title"]}: monthly cash buffer {d["cash_buffer"]["text"]}; change from current {delta["cash_buffer"]["text"]}; repayment-to-income {d["repayment_to_income"]["text"]}; savings coverage {d["savings_coverage"]["text"]}.']
            for k in ['repayment_to_income','savings_coverage']:
                if d[k]['text']=='N/A':parts.append(d[k]['reason'])
            parts.extend(m['message'] for m in s['messages'])
            specific=[a for a in s['assumptions'] if a not in common_assumptions]
            if specific:parts.append('Scenario assumption: '+' '.join(specific))
            segments.append({'id':'sim_'+s['key'],'variants':[' '.join(parts)]})
        segments.append({'id':'sim_assumptions','variants':['Shared assumptions: '+' '.join(common_assumptions)]})
        segments.append({'id':'sim_limits','variants':[SIM_LIMIT]})
    if not segments:raise ValueError('Supply a CFPB explanation, simulator output, or both')
    return segments


def explain_results(*,cfpb=None,simulator=None,llm_adapter=None):
    """Explain separate outputs; no model scoring, monetary formulas or external API."""
    segments=explanation_segments(cfpb=cfpb,simulator=simulator)
    digest=hashlib.sha256(json.dumps(segments,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
    choice=[{'id':s['id'],'variant':0} for s in segments];status='disabled';reason=None
    if llm_adapter is not None:choice,status,reason=llm_adapter.rewrite(deepcopy(segments),digest)
    lookup={s['id']:s for s in segments};sections=[{'id':c['id'],'text':lookup[c['id']]['variants'][c['variant']]} for c in choice]
    return {'status':'ok','mode':'template' if status=='disabled' else 'template_fallback' if status=='fallback' else 'validated_template_rewrite',
            'sections':sections,'text':'\n\n'.join(s['text'] for s in sections),'facts_digest':digest,'llm_status':status,'fallback_reason':reason,
            'llm_live_tested':False,'scope':'Structured results only; CFPB and simulator remain separate. No open-ended financial advice.'}
