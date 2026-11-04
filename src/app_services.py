"""Application adapters: cache trusted resources, never user inputs or results."""
from threading import RLock
from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
from .common import ROOT,read_json
from .cfpb_local_explanation import load_frozen,FrozenCFPBExplainer
from .extension_service import simulate_and_explain
from .result_explainer import explain_results
from .app_inputs import FIELDS

EVALUATION=Path('outputs/evaluation/stage5_v1')


def file_signature(paths):
    return tuple((str(p), (ROOT/p).stat().st_mtime_ns, (ROOT/p).stat().st_size) for p in paths)

@st.cache_resource(show_spinner=False)
def _prediction_resource(signature):
    freeze,model=load_frozen()
    return freeze,model,RLock()


def get_predictor():
    cfg=read_json('config/stage5_frozen.json')
    return _prediction_resource(file_signature([Path(cfg['artifact']),Path('config/stage5_frozen.json'),Path('config/feature_schema.json'),Path('data/splits/cfpb_split_ids.json')]))

@st.cache_resource(show_spinner=False)
def _explanation_resource(signature):return FrozenCFPBExplainer(),RLock()


def get_explainer():
    cfg=read_json('config/cfpb_shap_background.json');freeze=read_json('config/stage5_frozen.json')
    return _explanation_resource(file_signature([Path(cfg['background_file']),Path('config/cfpb_shap_background.json'),Path(freeze['artifact']),Path('config/feature_schema.json'),Path('data/splits/cfpb_split_ids.json')]))


def screen(codes):
    """Prediction survives a separate SHAP failure; never generate a fake explanation."""
    if not isinstance(codes,dict) or set(codes)!=set(FIELDS):return {'status':'invalid_input','errors':['Exactly eight survey-code inputs are required.']}
    try:
        for v in codes.values():
            if v is not None and (isinstance(v,(bool,str)) or not isinstance(v,(int,float)) or not np.isfinite(v)):raise ValueError('Invalid survey code')
        frame=pd.DataFrame([codes],columns=list(FIELDS)).astype(float)
    except (TypeError,ValueError):return {'status':'invalid_input','errors':['Use valid numeric survey codes or explicitly supported missing values.']}
    try:
        freeze,model,lock=get_predictor()
    except Exception:return {'status':'unavailable','errors':['The frozen screening model is unavailable. Stress remains available independently.']}
    try:
        with lock:
            classes=list(model.classes_)
            if classes!=[0,1]:raise RuntimeError('Unexpected positive-class mapping')
            probability=float(model.predict_proba(frame)[0,classes.index(1)])
    except ValueError:return {'status':'invalid_input','errors':['One or more survey codes are outside the frozen schema.']}
    except Exception:return {'status':'unavailable','errors':['Screening is temporarily unavailable. No estimate was generated.']}
    prediction={'probability':probability,'probability_display':f'{probability:.2%}','classification':int(probability>=freeze['threshold']),
                'threshold':freeze['threshold'],'positive_class':1,'label_meaning':read_json('config/label_mapping.json')['question'],
                'artifact_sha256':freeze['artifact_sha256']}
    result={'status':'ok','prediction':prediction,'local':None,'template':None,'messages':[]}
    try:
        explainer,explanation_lock=get_explainer()
        with explanation_lock:local=explainer.explain(codes)
        if abs(local['probability']-probability)>1e-12 or local['artifact_sha256']!=freeze['artifact_sha256']:raise RuntimeError('Explanation is not the submitted prediction')
        result['local']=local
    except Exception:
        result['status']='partial';result['messages'].append('Local explanation is temporarily unavailable. The screening estimate above is still valid; no contribution chart is shown.')
        return result
    try:result['template']=explain_results(cfpb=result['local'])
    except Exception:
        result['status']='partial';result['messages'].append('The template explanation is temporarily unavailable; the verified numerical results remain visible.')
    return result


def stress(payload,*,income_drop_percent,bnpl_reduction):
    """Only UI percent-to-fraction conversion; existing simulator owns every formula."""
    try:return simulate_and_explain(payload,income_drop=income_drop_percent/100,bnpl_reduction=bnpl_reduction)
    except Exception:return {'simulation':{'status':'unavailable','errors':[{'message':'Simulation is temporarily unavailable.'}],'scenarios':[]},'explanation':None}

@st.cache_data(show_spinner=False)
def _static_file(relative,signature):
    path=ROOT/relative
    return pd.read_csv(path) if path.suffix=='.csv' else json.loads(path.read_text()) if path.suffix=='.json' else path.read_text()


def evidence(relative):
    """Read known local evidence only; callers handle each missing file explicitly."""
    try:
        path=Path(relative)
        if path.is_absolute() or '..' in path.parts:raise ValueError('Project-relative evidence required')
        data=_static_file(str(path),file_signature([path]))
        return {'status':'ok','data':data}
    except Exception:return {'status':'unavailable','path':str(relative),'message':'This saved evidence file is unavailable. No placeholder result is substituted.'}
