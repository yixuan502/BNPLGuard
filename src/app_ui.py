"""English Screen/Stress/Explain/Model views over verified local interfaces."""
import os
from decimal import Decimal
from pathlib import Path
import pandas as pd
import streamlit as st
from .common import ROOT
from .installment_plan import calculate_plan
from . import app_services as services,app_state as state,app_charts as charts
from .app_inputs import FIELDS,LABELS,SHORT_LABELS,SCOPES,AMOUNTS,screen_options,screen_payload

TITLE='BNPLGuard — AI-Powered Financial Vulnerability Screening and BNPL Repayment Stress Simulation'
STYLE='''
<style>
.block-container {max-width:1080px; padding-top:1.7rem; padding-bottom:3rem;}
h1 {letter-spacing:-.04em; margin-bottom:0;}
h2 {letter-spacing:-.025em;}
[data-testid="stCaptionContainer"] {color:#506473;}
[data-testid="stMetric"] {background:#FFFFFF; border:1px solid #DFE7EC; border-radius:10px; padding:1rem;}
[data-testid="stMetricLabel"] p {white-space:normal; overflow:visible;}
[data-testid="stRadio"] [role="radiogroup"] {gap:1rem; flex-wrap:wrap;}
[data-testid="stAlert"] p {overflow-wrap:anywhere;}
@media (max-width:700px) {
 .block-container {padding:1rem .9rem 2rem;}
 h1 {font-size:2.2rem;}
 [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
 [data-testid="stColumn"] {min-width:100%; flex:1 1 100%;}
 [data-testid="stRadio"] [role="radiogroup"] {gap:.45rem;}
}
</style>
'''


def change_widget(section,field):
    state.change(st.session_state,section,field,st.session_state[section+'_widget_'+field])
    st.session_state.pop(section+'_error',None)


def reset_section(section):
    if section == 'stress':
        for key in ['plan_mode','plan_purchase','plan_upfront','plan_months','plan_applied','plan_manual']:
            st.session_state.pop(key, None)
    state.reset(st.session_state,section);st.session_state.pop(section+'_error',None)


def example_section(section,navigate=False):
    if section == 'stress':
        for key in ['plan_mode','plan_purchase','plan_upfront','plan_months','plan_applied','plan_manual']:
            st.session_state.pop(key, None)
    state.load_example(st.session_state,section);st.session_state.pop(section+'_error',None)
    if navigate:st.session_state['workspace']='Screen'


def restore_widgets(section):
    for field,value in st.session_state[section+'_draft'].items():
        key=section+'_widget_'+field
        if key not in st.session_state:st.session_state[key]=value


def get_evidence(relative):
    result=services.evidence(relative)
    if result['status']!='ok':st.warning(result['message']+' ('+Path(relative).name+')');return None
    return result['data']


def template_sections(template,ids=None):
    if not template:return
    for section in template['sections']:
        if ids is None or section['id'] in ids:
            text=section['text']
            for code,label in SHORT_LABELS.items():text=text.replace(code,label)
            st.markdown(text.replace('$',r'\$'))


def provenance_notice(section):
    if st.session_state[section+'_origin']=='fictional':st.info('Fictional example inputs are loaded. These are not the current user’s real financial information. Submit to calculate; edits stay within this session.')
    if st.session_state[section+'_changed']:st.info('Inputs changed. The previous result has been cleared; submit again to calculate.')


def render_screen_result(submission,*,details=True):
    result=submission['result'];prediction=result.get('prediction')
    if not prediction:return
    st.subheader('Submitted screening result')
    st.caption('Fictional example submission' if submission['origin']=='fictional' else 'Result for the eight submitted survey categories')
    st.metric('Estimated survey financial difficulty',prediction['probability_display'])
    st.write('The label means somewhat or very difficult to cover expenses and pay all bills in a typical month, rather than not at all difficult.')
    st.caption(f'Research class {prediction["classification"]} at the frozen {prediction["threshold"]} reference threshold. This is not a credit approval rule or a BNPL default probability.')
    for message in result.get('messages',[]):st.warning(message)
    local=result.get('local')
    if local:
        st.subheader('Contributions to this model estimate')
        st.altair_chart(charts.local_chart(local),width='stretch')
        st.caption('Positive contributions increase and negative contributions decrease this estimate relative to the training background. Units are log-odds, not probability percentage points. Contributions are not personal causes or causal effects.')
        st.markdown('**Template interpretation**')
        template_sections(result.get('template'),['cfpb_contributions'])
        if details:
            with st.expander('Submitted inputs and local explanation details'):
                rows=[{'Input':LABELS[r['feature']],'Submitted choice':r['raw_label'],'Imputed':r['imputed'],'SHAP (log-odds)':r['contribution_log_odds']} for r in local['contributions']]
                st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch')
                st.write('Background: '+str(local['background_n'])+' fixed training rows, seed 20261105. Independent masking breaks feature dependencies, including one-hot exclusivity.')
                st.write('Baseline plus eight contributions reproduces the model decision function; sigmoid reconstruction reproduces its probability.')
                st.json(local['checks'])
                template_sections(result.get('template'),['cfpb_estimate','cfpb_limits'])
    st.caption('Screening is based on a US survey model. Local probability overestimation and subgroup error differences remain documented in Model.')


def screen_page():
    st.header('Screen')
    st.write('Select the original survey categories. Screening uses annual household USD bands and survey responses; it is separate from the monthly Stress inputs.')
    actions=st.columns(2)
    actions[0].button('Load fictional example',key='screen_example',on_click=example_section,args=('screen',),width='stretch')
    actions[1].button('Reset screening',key='screen_reset',on_click=reset_section,args=('screen',),width='stretch')
    provenance_notice('screen');restore_widgets('screen')
    columns=st.columns(2)
    for i,field in enumerate(FIELDS):
        with columns[i%2]:
            options=screen_options(field)
            st.selectbox(LABELS[field],list(options),index=None,format_func=lambda value,opts=options:opts.get(value,'Choose an option'),
                key='screen_widget_'+field,placeholder='Choose an option',help=FIELDS[field]['question'],on_change=change_widget,args=('screen',field))
            st.caption(SCOPES[field])
            selected=st.session_state['screen_draft'][field]
            if selected is not None and len(options[selected])>32:st.caption('Selected: '+options[selected])
    st.caption('An explicit “use training imputation” option is available. Leaving a selection blank does not silently choose it.')
    if st.button('Run screening',type='primary',key='run_screen',width='stretch'):
        try:codes=screen_payload(st.session_state['screen_draft'])
        except ValueError as error:st.session_state['screen_error']=str(error)
        else:
            with st.spinner('Loading the frozen model and explaining this submission…'):result=services.screen(codes)
            if result['status'] in ['ok','partial']:state.commit(st.session_state,'screen',result)
            else:st.session_state['screen_error']=' '.join(result['errors'])
    if st.session_state.get('screen_error'):st.warning(st.session_state['screen_error'])
    submission=state.current_submission(st.session_state,'screen')
    if submission:render_screen_result(submission)
    else:st.info('No screening estimate has been calculated for the current inputs.')


def render_stress_result(submission):
    response=submission['result'];simulation=response['simulation']
    st.subheader('Scenario comparison')
    st.caption('Illustrative scenario—not empirical model results. '+('Fictional example submission.' if submission['origin']=='fictional' else 'Results for the submitted assumptions.'))
    inputs=submission['inputs']
    st.write(f"Submitted assumptions: {inputs['currency']}; income reduction {inputs['income_drop_percent']:g}%; "
             f"proposed new monthly BNPL {inputs['currency']} {inputs['Bnew']:,.2f}; "
             f"hypothetical reduction of existing monthly BNPL {inputs['currency']} {inputs['bnpl_reduction']:,.2f}.")
    st.caption('Final monthly cash buffer is the amount left after expenses and repayments. Change from current is the difference from the Current scenario, not the final amount.')
    # Single-column cards preserve reading order at every viewport width.
    for item in simulation['scenarios']:
        buffer=Decimal(item['metrics']['cash_buffer']['value'])
        status='Surplus' if buffer>0 else 'Shortfall' if buffer<0 else 'Break-even'
        with st.container(border=True):
            st.markdown('**'+item['title']+'**')
            st.write('Final monthly cash buffer: '+item['display']['cash_buffer']['text'])
            st.write('Change from current: '+item['delta_display']['cash_buffer']['text'])
            st.write('Status: '+status)
    st.altair_chart(charts.stress_chart(simulation),width='stretch')
    st.markdown('**Scenario details: RTI, savings coverage and explanation**')
    scenarios={s['title']:s for s in simulation['scenarios']}
    selected=st.selectbox('Inspect a scenario',list(scenarios),key='stress_inspect')
    scenario=scenarios[selected]
    cols=st.columns(3)
    for col,key,title in zip(cols,['cash_buffer','repayment_to_income','savings_coverage'],['Monthly cash buffer','Repayment-to-income','Savings coverage']):
        value=scenario['display'][key];delta=scenario['delta_display'][key]
        with col:
            st.metric(title,value['text'],delta=None if delta['text']=='N/A' else delta['text'],delta_color='off',delta_arrow='off')
            st.caption('Change from current' if key!='repayment_to_income' else 'Change from current, in percentage points')
            if value['reason']:st.caption(value['reason'])
            if delta['reason']:st.caption('Change unavailable: '+delta['reason'])
    st.markdown('**Template interpretation**')
    template_sections(response.get('explanation'),['sim_'+scenario['key']])
    st.caption('These financial calculations do not change the CFPB screening estimate. A positive monthly buffer does not guarantee cash on every payment due date. A repayment reduction is hypothetical, not permission to change a contract.')
    with st.expander('All scenario values, assumptions and complete template explanation'):
        for s in simulation['scenarios']:
            st.markdown('**'+s['title']+'**')
            for k,title in [('cash_buffer','Buffer'),('repayment_to_income','RTI'),('savings_coverage','Coverage')]:
                st.write(title+': '+s['display'][k]['text']+'; change: '+s['delta_display'][k]['text'])
        template_sections(response.get('explanation'),['sim_assumptions','sim_limits'])
        st.write('Savings coverage assumes no new income and constant expenses/repayments; it is not actual time until funds run out. No dated payment calendar, fees or multi-month depletion are modeled.')


def plan_mode_changed():
    ss=st.session_state
    if ss['plan_mode']=='Estimate from a purchase plan':
        ss['plan_manual']=ss['stress_draft']['Bnew']
        value=None
        ss.pop('plan_applied',None)
    else:
        value=ss.get('plan_manual')
        ss.pop('plan_applied',None)
    ss['stress_widget_Bnew']=value
    state.change(ss,'stress','Bnew',value)
    ss.pop('stress_submission',None)
    ss['stress_changed']=True


def plan_edited():
    ss=st.session_state
    ss.pop('plan_applied',None)
    ss['stress_widget_Bnew']=None
    state.change(ss,'stress','Bnew',None)
    ss.pop('stress_submission',None)
    ss['stress_changed']=True


def apply_plan():
    ss=st.session_state
    try:
        plan=calculate_plan(ss['plan_purchase'],ss['plan_upfront'],ss['plan_months'])
        value=float(plan['maximum'])
        ss['stress_widget_Bnew']=value
        state.change(ss,'stress','Bnew',value)
        ss['plan_applied']=(ss['plan_purchase'],ss['plan_upfront'],ss['plan_months'])
        ss.pop('stress_submission',None)
        ss['stress_changed']=True
    except ValueError as error:
        ss['stress_error']=str(error)


def stress_page():
    st.header('Stress')
    st.write('Compare monthly repayment assumptions. Use one currency throughout; no exchange-rate conversion is performed. Necessary living expenses must exclude all repayments entered separately.')
    actions=st.columns(2)
    actions[0].button('Load fictional financial example',key='stress_example',on_click=example_section,args=('stress',),width='stretch')
    actions[1].button('Reset simulation',key='stress_reset',on_click=reset_section,args=('stress',),width='stretch')
    provenance_notice('stress');restore_widgets('stress')
    st.selectbox('Currency for every amount',['AUD','USD','EUR','GBP','CAD','INR'],key='stress_widget_currency',on_change=change_widget,args=('stress','currency'))
    st.subheader('Monthly cash flow')
    st.caption('Enter each amount once: living expenses exclude debt repayments; non-BNPL debt excludes BNPL; existing BNPL excludes the proposed new plan.')
    for field,(label,help_text) in AMOUNTS.items():
        if field=='Bnew':
            mode=st.radio('Proposed new BNPL input', ['Enter monthly repayment directly','Estimate from a purchase plan'], key='plan_mode', on_change=plan_mode_changed)
            if mode=='Estimate from a purchase plan':
                st.caption('One payment per month; no interest or fees. The upfront payment was paid before the simulated month. Enter savings after that payment. Results describe one instalment month, not the purchase-day cash flow. This is a budget estimate, not a provider quote, approval or default probability. Amounts must use the selected currency and whole cents.')
                st.number_input('Purchase amount', min_value=0.0, value=None, step=0.01, format='%.2f', key='plan_purchase', on_change=plan_edited)
                st.number_input('Upfront payment', min_value=0.0, value=0.0, step=0.01, format='%.2f', key='plan_upfront', on_change=plan_edited)
                st.number_input('Number of monthly instalments', min_value=1, value=3, step=1, key='plan_months', on_change=plan_edited)
                try:
                    plan=calculate_plan(st.session_state.plan_purchase,st.session_state.plan_upfront,st.session_state.plan_months)
                    currency=st.session_state.stress_draft['currency']
                    st.write(f"Remaining instalment principal: {currency} {plan['remaining']:.2f}")
                    st.write(f"Regular monthly repayment: {currency} {plan['regular']:.2f}")
                    if plan['final'] != plan['regular']:
                        st.write(f"Final instalment repayment: {currency} {plan['final']:.2f}")
                    st.write(f"Monthly repayment used in this scenario: {currency} {plan['maximum']:.2f}")
                    st.caption('The highest repayment month is used; other months may be slightly lower. The first N−1 payments are rounded down to cents; the last payment clears the remainder.')
                    st.button('Use this repayment in the stress simulator',key='apply_plan',on_click=apply_plan)
                except ValueError as error:
                    st.info(str(error))
                if not st.session_state.get('plan_applied'):
                    st.info('Apply the current purchase plan before comparing scenarios.')
                else:
                    st.success('Purchase plan repayment applied. Compare scenarios to calculate.')
                continue
        if field=='S':
            st.subheader('Savings balance today')
            st.write('Savings are not included in monthly income or the monthly cash buffer. They are used to calculate how many months of expenses and repayments could be covered with no new income and unchanged outflows.')
        st.number_input(label,min_value=0.,value=None,step=50.,format='%.2f',key='stress_widget_'+field,
            placeholder='Enter amount (zero is valid)',help=help_text,on_change=change_widget,args=('stress',field))
        st.caption(help_text)
    st.subheader('Scenario assumptions')
    st.slider('Assumed income reduction (%)',min_value=0.,max_value=100.,step=5.,key='stress_widget_income_drop_percent',on_change=change_widget,args=('stress','income_drop_percent'))
    st.number_input('Hypothetical reduction of existing monthly BNPL',min_value=0.,step=50.,format='%.2f',key='stress_widget_bnpl_reduction',
          help='Cannot exceed existing BNPL. This is a scenario assumption, not a contract change.',on_change=change_widget,args=('stress','bnpl_reduction'))
    if st.button('Compare scenarios',type='primary',key='run_stress',width='stretch'):
        draft=st.session_state['stress_draft'];payload={k:draft[k] for k in AMOUNTS};payload['currency']=draft['currency']
        with st.spinner('Calculating the five independent scenarios…'):response=services.stress(payload,income_drop_percent=draft['income_drop_percent'],bnpl_reduction=draft['bnpl_reduction'])
        if response['simulation']['status'] in ['ok','partial']:state.commit(st.session_state,'stress',response)
        else:st.session_state['stress_error']=' '.join(e.get('message','Invalid input') for e in response['simulation']['errors'])
    if st.session_state.get('stress_error'):st.warning(st.session_state['stress_error'])
    submission=state.current_submission(st.session_state,'stress')
    if submission:render_stress_result(submission)
    else:st.info('No scenario result has been calculated for the current inputs.')


def explain_page():
    st.header('Explain')
    st.write('Three different kinds of explanation answer different questions. None establishes causality.')
    global_tab,local_tab,scenario_tab=st.tabs(['Global','Local','Scenario'])
    with global_tab:
        st.subheader('What matters across validation records?')
        st.write('Permutation Importance measures the saved mean decrease in validation Average Precision when each original input is shuffled. It is not an individual explanation.')
        frame=get_evidence(services.EVALUATION/'validation_permutation_importance.csv')
        if frame is not None:st.altair_chart(charts.importance_chart(frame),width='stretch')
        with st.expander('Global method and variability'):
            st.write('The existing analysis used 30 repeats on validation data and the entire frozen Pipeline. Correlated inputs and unrealistic shuffled combinations limit interpretation. No explanation was recomputed on the full dataset.')
            if frame is not None:st.dataframe(frame,hide_index=True,width='stretch')
    with local_tab:
        st.subheader('What contributes to this submitted estimate?')
        submission=state.current_submission(st.session_state,'screen')
        if submission:render_screen_result(submission)
        else:
            st.info('Submit Screen first. No personal contribution chart is available for the current inputs.')
            st.button('Load example inputs in Screen',key='explain_example',on_click=example_section,args=('screen',True),width='stretch')
        with st.expander('Local SHAP method'):
            st.write('Actual SHAP LinearExplainer uses 200 fixed training rows, seed 20261105. Contributions are in log-odds and are grouped from encoded columns into eight original inputs. A different background may change attribution without changing the prediction. Independent masking breaks dependence between inputs; these are model contributions, not financial causes or recommended actions.')
    with scenario_tab:
        st.subheader('How do assumptions change cash flow?')
        submission=state.current_submission(st.session_state,'stress')
        if submission:render_stress_result(submission)
        else:st.info('Submit Stress to compare its five scenarios. Scenario arithmetic is independent of the survey model.')
        with st.expander('Monthly formulas and assumptions'):
            st.latex(r'B=B_0+B_{new},\quad Buffer=I-E-D-B')
            st.latex(r'RTI=(D+B)/I,\quad Coverage=S/(E+D+B)')
            st.write('I is after-tax monthly income, E necessary expenses excluding separately counted repayments, D non-BNPL repayments, B0 existing BNPL, Bnew proposed BNPL and S available savings. Zero denominators return explained N/A; cash flow remains calculable. Coverage is months under no new income and unchanged outflows, not actual depletion time.')
    st.caption('Interpretation is generated by reviewed English rule templates. This application has no LLM chatbot or enabled external LLM connection.')


def number(value,precision=4):return 'N/A' if value is None or pd.isna(value) else f'{value:.{precision}f}'

def metric_table(results):
    names={'logistic_regression':'Frozen LR','dummy':'Dummy','random_forest':'RF'}
    rows=['| Metric | Frozen LR | Dummy | RF |','|---|---:|---:|---:|']
    for key,label in [('accuracy','Accuracy'),('precision','Precision'),('recall','Recall'),('f1','F1'),('roc_auc','ROC-AUC'),('average_precision','AP'),('brier','Brier')]:
        rows.append('| '+label+' | '+' | '.join(number(results[n][key]) for n in names)+' |')
    return '\n'.join(rows)


def model_page():
    st.header('Model')
    st.write('Research evidence for the frozen survey model. Published test results are read from saved artifacts; opening this page does not train, bootstrap or evaluate a model.')
    source=get_evidence('config/app_source.json');label=get_evidence('config/label_mapping.json');split=get_evidence('data/splits/cfpb_split_ids.json')
    if source:
        st.markdown(f'**Source:** [CFPB National Financial Well-Being Survey]({source["landing_url"]}), {source["survey_year"]} US survey; release {source["release"]}.')
    if label:st.write('**Label:** '+label['question']+' Codes 2/3 (somewhat/very difficult) are class 1; code 1 is class 0. Missing labels were excluded.')
    if split:st.caption('Locked split: '+', '.join(f'{k} {len(split[k]):,}' for k in ['train','validation','test'])+'. Eight original survey inputs; threshold 0.5; no extra probability calibration.')
    test=get_evidence(services.EVALUATION/'test_metrics.json')
    if test:
        lr=test['logistic_regression'];cols=st.columns(3)
        for col,key,title in zip(cols,['average_precision','roc_auc','brier'],['Test AP','Test ROC-AUC','Test Brier']):col.metric(title,number(lr[key]))
        st.caption(f'Test n = {lr["n"]:,}; positives = {lr["positive_n"]:,}; positive share = {lr["positive_rate"]:.2%}. Primary results are unweighted.')
        with st.expander('All test metrics and prespecified comparators'):
            st.markdown(metric_table(test));st.caption('Threshold 0.5 for all classification metrics. Dummy Precision is N/A because it predicts no positives. RF is a prespecified comparator; test results do not reopen model selection.')
    intervals=get_evidence(services.EVALUATION/'bootstrap_intervals.json')
    if intervals and test:
        with st.expander('Main 95% intervals and uncertainty scope'):
            for key,label_text in [('average_precision','AP'),('roc_auc','ROC-AUC'),('brier','Brier'),('recall','Recall'),('f1','F1')]:
                interval=intervals['logistic_regression'][key];st.write(label_text+': ['+number(interval['lower'])+', '+number(interval['upper'])+']')
            st.write('2,000 paired ordinary respondent bootstrap draws, seed 20261104. These intervals reflect the fixed model and current empirical test sample, not the full training/selection process, complex survey design or Australian transportability.')
    discrimination,reliability,groups=st.tabs(['ROC / PR','Reliability','Groups / weights'])
    with discrimination:
        curve=st.radio('Saved curve',['ROC','PR'],horizontal=True,key='model_curve')
        frames=[];kind=curve.lower()
        for name,display in [('logistic_regression','LR'),('dummy','Dummy'),('random_forest','RF')]:
            frame=get_evidence(services.EVALUATION/f'{name}_{kind}.csv')
            if frame is not None:
                keys=['fpr','tpr'] if kind=='roc' else ['recall','precision'];part=frame[keys].copy();part['Model']=display;frames.append(part)
        if frames:st.altair_chart(charts.discrimination_chart(pd.concat(frames,ignore_index=True),kind),width='stretch')
    with reliability:
        st.write('Some probability bins show local overestimation. Neither the lack of extra calibration nor a lower Brier score proves calibration quality.')
        cal=get_evidence(services.EVALUATION/'lr_calibration_bins.csv')
        if cal is not None:
            st.altair_chart(charts.calibration_chart(cal),width='stretch')
            st.caption(f'Ten equal-width bins; saved bin counts range from {cal.n.min()} to {cal.n.max()}. Vertical bars are descriptive Wilson intervals. These are not Australian validation estimates.')
            with st.expander('Saved calibration bins'):st.dataframe(cal,hide_index=True,width='stretch')
    with groups:
        st.write('Subgroup errors differ. Similar scores would not establish absence of bias, and these differences alone do not establish causal discrimination.')
        frame=get_evidence(services.EVALUATION/'subgroup_metrics.csv')
        if frame is not None:
            scheme=st.selectbox('Audit grouping',['age_primary','income_primary'],format_func=lambda x:'Age groups' if x=='age_primary' else 'Annual household income (USD)',key='model_group')
            selected=frame[(frame.model=='logistic_regression')&(frame.scheme==scheme)]
            for row in selected.to_dict('records'):
                with st.container(border=True):
                    st.markdown('**'+str(row['group'])+'**')
                    st.write(f'n = {row["n"]}; positive = {row["positive_n"]}; negative = {row["negative_n"]}. Recall {number(row["recall"])}; false positive rate {number(row["false_positive_rate"])}.')
                    st.caption('Descriptive group results; single-class or small groups have limited precision. No group-specific threshold was optimized.')
        st.markdown('**Survey weights**')
        st.write('Training and main evaluation are unweighted. finalwt sensitivity is separate and does not provide complete complex-survey inference.')
        weighted=get_evidence(services.EVALUATION/'weighted_test_sensitivity.json')
        if weighted:
            w=weighted['logistic_regression'];st.caption(f'Saved finalwt-weighted sensitivity: AP {number(w["average_precision"])}, ROC-AUC {number(w["roc_auc"])}, Brier {number(w["brier"])}; weighted positive share {w["positive_rate"]:.2%}.')
    with st.expander('Features, validation selection and model cards'):
        st.write('The validation selection retained raw Logistic Regression for probability error, simplicity and interpretation; the feature set and fixed 0.5 threshold were frozen before test access. No refit, test-driven calibration or reselection followed.')
        for key in FIELDS:st.write('**'+LABELS[key]+'** — '+FIELDS[key]['question'])
        selection=get_evidence('docs/model_selection.md')
        if selection:st.markdown(selection)
        card=get_evidence('docs/model_card.md')
        if card:st.markdown('### Original stage-five research card (versioned evidence)');st.markdown(card)
        addendum=get_evidence('docs/model_card_extensions.md')
        if addendum:st.markdown(addendum)
    with st.expander('Additional research / Data selection'):
        st.write('Kaggle independent recorded-label classification is complete. Definition/timing gaps and generalization limits keep it in the report appendix. It supplies no personal prediction here, is not CFPB external validation, and is never combined with this model’s probability. Different-task AUC values do not rank the datasets.')
        st.caption('The application has no Kaggle personal-input form and no enabled LLM connection.')
    with st.expander('Australian background: official sources'):
        st.write('Business context only: these sources are not Australian model validation or compliance certification, and define no simulator risk cutoff.')
        register=get_evidence('docs/references/australia_2026-11-05/source_register.json')
        if register:
            for entry in register['sources']:
                st.markdown('**['+entry['title']+']('+entry['url']+')**')
                st.caption('Published/version: '+entry['published_on']+' · Accessed '+entry['accessed_on'])
                st.write(entry['supports']);st.caption(entry['limit'])


def main():
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'outputs/.mplconfig'))
    st.set_page_config(page_title=TITLE,page_icon='◈',layout='wide',initial_sidebar_state='collapsed')
    state.initialize(st.session_state)
    st.markdown(STYLE,unsafe_allow_html=True)
    st.title('BNPLGuard')
    st.caption('AI-Powered Financial Vulnerability Screening and BNPL Repayment Stress Simulation')
    st.caption('Release: stress-installments-20261105')
    page=st.radio('Workspace',['Screen','Stress','Explain','Model'],horizontal=True,key='workspace',label_visibility='collapsed')
    st.divider()
    {'Screen':screen_page,'Stress':stress_page,'Explain':explain_page,'Model':model_page}[page]()
    st.divider()
    st.caption('Research prototype · Inputs and results are session-scoped on the application server; no financial-input logs or external API transmission. Template explanations only; LLM disabled. No credit decisions or Australian external-validation claim.')
