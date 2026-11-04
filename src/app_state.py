"""Session-only draft/submission lifecycle, independent of Streamlit rendering."""
from copy import deepcopy
from .app_inputs import FIELDS,AMOUNTS,screening_example,stress_example


def initialize(state):
    if 'screen_draft' not in state:state['screen_draft']={k:None for k in FIELDS}
    if 'stress_draft' not in state:state['stress_draft']={**{k:None for k in AMOUNTS},'currency':'AUD','income_drop_percent':20.0,'bnpl_reduction':0.0}
    for section in ['screen','stress']:
        if section+'_origin' not in state:state[section+'_origin']='empty'
        if section+'_changed' not in state:state[section+'_changed']=False


def change(state,section,field,value):
    draft=deepcopy(state[section+'_draft'])
    if draft[field]!=value:
        draft[field]=value;state[section+'_draft']=draft
        state.pop(section+'_submission',None);state[section+'_changed']=True


def reset(state,section):
    state.pop(section+'_submission',None);state[section+'_changed']=False;state[section+'_origin']='empty'
    if section=='screen':draft={k:None for k in FIELDS}
    else:draft={**{k:None for k in AMOUNTS},'currency':'AUD','income_drop_percent':20.0,'bnpl_reduction':0.0}
    state[section+'_draft']=draft
    for field,value in draft.items():state[section+'_widget_'+field]=value


def load_example(state,section):
    reset(state,section);draft=screening_example() if section=='screen' else stress_example()
    state[section+'_draft']=deepcopy(draft);state[section+'_origin']='fictional'
    for field,value in draft.items():state[section+'_widget_'+field]=value


def commit(state,section,result):
    state[section+'_submission']={'inputs':deepcopy(state[section+'_draft']),'result':deepcopy(result),'origin':state[section+'_origin']}
    state[section+'_changed']=False


def current_submission(state,section):
    submission=state.get(section+'_submission')
    if submission and submission['inputs']==state[section+'_draft']:return submission
    if submission:state.pop(section+'_submission',None);state[section+'_changed']=True
    return None
