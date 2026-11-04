"""Portable raw-data-free app smoke test, run from a clean release checkout."""
from pathlib import Path
import json,os,sys,time
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT);sys.path.insert(0,str(ROOT))
START=time.monotonic()
from streamlit.testing.v1 import AppTest
from src.common import ROOT as ACTUAL_ROOT,read_json
assert ACTUAL_ROOT==ROOT
assert not (ROOT/'data/raw').exists(),'Clean release must not contain raw data'
at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run();assert not at.exception and not at.metric
at.button(key='screen_example').click().run();at.button(key='run_screen').click().run();assert not at.exception
screen=at.session_state['screen_submission']['result'];assert screen['status']=='ok' and screen['local'] is not None and screen['template']['llm_status']=='disabled'
assert screen['prediction']['probability']==screen['local']['probability']
assert max(screen['local']['checks'].values())<1e-10
at.radio(key='workspace').set_value('Stress').run();at.button(key='stress_example').click().run();at.button(key='run_stress').click().run();assert not at.exception
sim=at.session_state['stress_submission']['result']['simulation'];values=[s['metrics']['cash_buffer']['value'] for s in sim['scenarios']]
assert values==['900','700','0','-200','1100']
at.radio(key='workspace').set_value('Explain').run();assert not at.exception
at.radio(key='workspace').set_value('Model').run();assert not at.exception
assert not any('unavailable' in w.value.lower() for w in at.warning)
assert [m.value for m in at.metric]==['0.7634','0.8432','0.1573']
print(json.dumps({'status':'PASS','elapsed_seconds':round(time.monotonic()-START,3),'runtime_root':str(ROOT),'raw_csv_present':False,'screen_probability':screen['prediction']['probability'],'shap_errors':screen['local']['checks'],'simulator_buffers':values,'model_metrics':[m.value for m in at.metric],'areas':['Screen','Stress','Explain','Model'],'llm':'disabled'},indent=2))
