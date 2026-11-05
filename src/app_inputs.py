"""Schema-derived display options and UI units; never invent survey money mappings."""
from copy import deepcopy
from .common import read_json

MISSING='__explicit_missing__'
FIELDS=read_json('config/feature_schema.json')['features']
LABELS={
    'PPINCIMP':'Annual household income (USD)',
    'SAVINGSRANGES':'Savings today (USD)',
    'EMPLOY':'Your primary work status',
    'VOLATILITY':'Household income pattern',
    'EARNERS':'Household income contributors',
    'HOUSING':'Housing situation',
    'PRODHAVE_8':'Student / education loan',
    'PPHHSIZE':'People in your household',
}
SHORT_LABELS={'PPINCIMP':'Income','SAVINGSRANGES':'Savings','EMPLOY':'Work status','VOLATILITY':'Income pattern','EARNERS':'Contributors','HOUSING':'Housing','PRODHAVE_8':'Education loan','PPHHSIZE':'Household size'}
SCOPES={
    'PPINCIMP':'Annual household income bands in USD; not monthly take-home income.',
    'SAVINGSRANGES':'Respondent-reported cash, checking and savings balances today, in USD bands.',
    'EMPLOY':'Your own status. The frozen model groups the non-paid-work categories together.',
    'VOLATILITY':'How household income changes from month to month.',
    'EARNERS':'People contributing to the income used to pay household bills.',
    'HOUSING':'Your current housing arrangement.',
    'PRODHAVE_8':'A student/education loan for yourself or someone else.',
    'PPHHSIZE':'Household members; the final band is five or more.',
}
AMOUNTS={'I':('Monthly after-tax income','Income received after tax each month. Do not include savings balances.'),
         'E':('Monthly necessary living expenses','Living costs only. Exclude all debt and BNPL repayments entered below.'),
         'D':('Monthly non-BNPL debt repayments','Existing debt repayments per month, excluding all BNPL repayments.'),
         'B0':('Monthly existing BNPL repayments','Total repayments per month on existing BNPL commitments. Exclude the proposed new plan.'),
         'Bnew':('Monthly proposed new BNPL repayments','Additional repayments per month for the proposed plan, not its purchase price.'),
         'S':('Emergency savings — current available balance','Available savings today, not monthly income or a monthly contribution.')}



def screen_options(field):
    meta=FIELDS[field]
    options={str(code):label for code,label in meta['labels'].items()}
    options.update({str(code):label+' — training imputation' for code,label in meta['missing_codes'].items()})
    # The frozen Pipeline supports ordinary missing values for every field.
    options[MISSING]='Prefer not to answer — use training imputation'
    return options


def screen_payload(selections):
    if set(selections)!=set(FIELDS):raise ValueError('Exactly eight screening fields required')
    absent=[LABELS[k] for k,v in selections.items() if v is None]
    if absent:raise ValueError('Complete each selection, or explicitly choose imputation: '+', '.join(absent))
    result={}
    for k,v in selections.items():
        if v not in screen_options(k):raise ValueError('Unknown screening option')
        result[k]=None if v==MISSING else int(v)
    return result


def screening_example():
    fixture=read_json('config/app_examples.json')['screen']
    return {k:str(v) for k,v in fixture.items()}


def stress_example():
    cfg=read_json('config/simulator_demo.json');p=deepcopy(cfg['fictional_inputs'])
    return {**p,'income_drop_percent':cfg['scenario_settings']['income_drop']*100,'bnpl_reduction':cfg['scenario_settings']['bnpl_reduction']}
