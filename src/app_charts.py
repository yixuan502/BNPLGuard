"""Charts of existing structured outputs and saved evidence; no model/statistical fitting."""
import altair as alt
import pandas as pd
from .app_inputs import SHORT_LABELS

COLORS={'LR':'#176B87','Dummy':'#68737D','RF':'#C58223'}
SCENARIO_LABELS={'current':'Current','added_bnpl':'New BNPL','income_shock':'Income shock','added_bnpl_income_shock':'Combined','reduced_existing_bnpl':'Reduced BNPL'}


def local_chart(local):
    frame=pd.DataFrame([{'Input':SHORT_LABELS[r['feature']],'Contribution':r['contribution_log_odds'],'Value':r['raw_label'],
                         'Signed':f'{r["contribution_log_odds"]:+.3f}'} for r in local['contributions']])
    order=frame.reindex(frame.Contribution.abs().sort_values(ascending=False).index).Input.tolist()
    base=alt.Chart(frame).encode(y=alt.Y('Input:N',sort=order,title=None,axis=alt.Axis(labelLimit=130)),
                               x=alt.X('Contribution:Q',title='SHAP contribution (log-odds)',scale=alt.Scale(zero=True)),
                               tooltip=['Input:N','Value:N',alt.Tooltip('Contribution:Q',format='+.4f')])
    bars=base.mark_bar(size=18).encode(color=alt.condition(alt.datum.Contribution>=0,alt.value('#176B87'),alt.value('#C58223')))
    zero=alt.Chart(pd.DataFrame({'zero':[0]})).mark_rule(color='#465562',strokeWidth=1).encode(x='zero:Q')
    return (bars+zero).properties(height=265)


def stress_chart(simulation):
    rows=[{'Scenario':SCENARIO_LABELS[s['key']],'Cash buffer':float(s['metrics']['cash_buffer']['value']),
           'Amount':s['display']['cash_buffer']['text']} for s in simulation['scenarios']]
    frame=pd.DataFrame(rows);order=list(SCENARIO_LABELS.values())
    bars=alt.Chart(frame).mark_bar(size=24).encode(y=alt.Y('Scenario:N',sort=order,title=None,axis=alt.Axis(labelLimit=130)),
        x=alt.X('Cash buffer:Q',title='Monthly cash buffer ('+simulation['currency']+')',scale=alt.Scale(zero=True)),
        color=alt.condition(alt.datum['Cash buffer']>=0,alt.value('#176B87'),alt.value('#C58223')),tooltip=['Scenario:N','Amount:N'])
    zero=alt.Chart(pd.DataFrame({'zero':[0]})).mark_rule(color='#122936',strokeWidth=1).encode(x='zero:Q')
    return (bars+zero).properties(height=230)


def importance_chart(frame):
    frame=frame.copy();frame['Input']=frame.feature.map(SHORT_LABELS)
    return alt.Chart(frame).mark_bar(color='#176B87',size=18).encode(y=alt.Y('Input:N',sort='-x',title=None,axis=alt.Axis(labelLimit=130)),
          x=alt.X('mean_ap_drop:Q',title='Mean validation AP decrease',scale=alt.Scale(zero=True)),
          tooltip=['Input:N',alt.Tooltip('mean_ap_drop:Q',format='.4f'),alt.Tooltip('sd_ap_drop:Q',format='.4f')]).properties(height=265)


def discrimination_chart(frame,kind):
    x,y=('fpr','tpr') if kind=='roc' else ('recall','precision')
    return alt.Chart(frame).mark_line().encode(x=alt.X(x+':Q',title='False positive rate' if kind=='roc' else 'Recall',scale=alt.Scale(domain=[0,1])),
         y=alt.Y(y+':Q',title='True positive rate' if kind=='roc' else 'Precision',scale=alt.Scale(domain=[0,1])),
         color=alt.Color('Model:N',scale=alt.Scale(domain=list(COLORS),range=list(COLORS.values())),legend=alt.Legend(orient='top')),
         strokeDash=alt.StrokeDash('Model:N',legend=None),order=alt.Order(x+':Q'),tooltip=['Model:N',alt.Tooltip(x+':Q',format='.3f'),alt.Tooltip(y+':Q',format='.3f')]).properties(height=285)


def calibration_chart(frame):
    frame=frame[frame.n>0].copy()
    points=alt.Chart(frame).mark_point(color='#176B87',filled=True,size=65).encode(
        x=alt.X('mean_prediction:Q',title='Mean estimated probability',scale=alt.Scale(domain=[0,1])),
        y=alt.Y('observed_rate:Q',title='Observed difficulty share',scale=alt.Scale(domain=[0,1])),
        tooltip=['n:Q',alt.Tooltip('mean_prediction:Q',format='.3f'),alt.Tooltip('observed_rate:Q',format='.3f')])
    interval=alt.Chart(frame).mark_rule(color='#6D8794').encode(x='mean_prediction:Q',y='observed_wilson_lower:Q',y2='observed_wilson_upper:Q')
    reference=alt.Chart(pd.DataFrame({'x':[0.,1.],'y':[0.,1.]})).mark_line(color='#68737D',strokeDash=[4,4]).encode(x='x:Q',y='y:Q')
    return (reference+interval+points).properties(height=300)
