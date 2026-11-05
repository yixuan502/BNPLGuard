from pathlib import Path
import sys,json,hashlib
r=Path(__file__).resolve().parents[3];sys.path.insert(0,str(r))
from src.simulator_presentation import run_simulation
cases={'A':dict(I=4000,E=2200,D=600,B0=300,Bnew=200,S=800),'B':dict(I=5000,E=2800,D=700,B0=400,Bnew=300,S=1200)}
verified={}
for key,p in cases.items():
    result=run_simulation(p,income_drop=0.2,bnpl_reduction=0)
    by={s['key']:s for s in result['scenarios']}
    print(key,[(s['key'],s['metrics']['cash_buffer']['value'],s['delta_from_current']['cash_buffer']['value']) for s in result['scenarios']])
    verified[key]={'inputs':p,'income_drop':0.2,'bnpl_reduction':0,'result':result}
json.dump(verified,open(r/'user_testing/materials_v1/cases_verified.json','w'),indent=2)
print('Model unchanged',hashlib.sha256((r/'models/cfpb/stage4_v1/logistic_regression.joblib').read_bytes()).hexdigest())
