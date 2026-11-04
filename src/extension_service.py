"""Stable integration entry points. No Streamlit, refitting or external API."""
import argparse
from functools import lru_cache
from .common import ROOT,read_json,write_json,sha256
from .cfpb_local_explanation import FrozenCFPBExplainer
from .simulator_presentation import run_simulation
from .result_explainer import explain_results

@lru_cache(maxsize=1)
def get_cfpb_explainer():return FrozenCFPBExplainer()


def predict_and_explain_cfpb(raw_survey_codes):
    try:return get_cfpb_explainer().explain(raw_survey_codes)
    except (TypeError,ValueError) as error:return {'status':'invalid_input','errors':[str(error)]}


def simulate_and_explain(amounts,*,income_drop=.2,bnpl_reduction=0):
    result=run_simulation(amounts,income_drop=income_drop,bnpl_reduction=bnpl_reduction)
    return {'simulation':result,'explanation':None if result['status']=='invalid_input' else explain_results(simulator=result)}


def load_kaggle_research_summary(*,include_appendix=False):
    """Report-appendix reader only; never a personal prediction or default app tab."""
    if not include_appendix:return {'status':'not_in_application','presentation':'Report appendix only','personal_prediction_enabled':False}
    from .kaggle_experiment import verify,DEFAULT_RUN,DEFAULT_OUT
    freeze=verify(DEFAULT_RUN,DEFAULT_OUT)
    return {'status':'appendix_only','objective':'Exploratory classification of the recorded default_flag label in the Kaggle dataset.',
            'selected_model':freeze['selected_model'],'threshold':freeze['threshold'],'test_metrics':read_json(ROOT/DEFAULT_OUT/'test_metrics.json'),
            'personal_prediction_enabled':False,'limitations':'Unverified origin, field timing and default window; not CFPB external validation or real Australian default evidence.'}


def demo(output_dir='outputs/extensions/demo_v1'):
    out=ROOT/output_dir
    if out.exists():raise FileExistsError('Preserve completed demo; choose a new --output-dir')
    out.mkdir(parents=True);baseline=read_json('data/metadata/extensions_baseline.json');cfpb=predict_and_explain_cfpb(baseline['cfpb_inputs'][0])
    simulation=run_simulation({'I':4500,'E':2500,'D':700,'B0':400,'Bnew':200,'S':1000},income_drop=.2,bnpl_reduction=200)
    explanation=explain_results(cfpb=cfpb,simulator=simulation)
    write_json(out/'cfpb.json',cfpb);write_json(out/'simulation.json',simulation);write_json(out/'explanation.json',explanation)
    (out/'explanation.txt').write_text(explanation['text']+'\n')
    write_json(out/'manifest.json',{'fictional_inputs_only':True,'live_llm_called':False,'adapter_status':'LLM adapter prepared, not live-tested','files_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file()}})
    print(explanation['text']);print('\nLLM adapter prepared, not live-tested.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',default='outputs/extensions/demo_v1');a=p.parse_args();demo(a.output_dir)
