"""Training-background SHAP for the frozen CFPB LR; never fits an estimator."""
import argparse
import os
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy.special import expit
from .common import ROOT,read_json,write_json,sha256

BACKGROUND_CONFIG='config/cfpb_shap_background.json'
BACKGROUND_FILE='models/cfpb/explanations_v1/background_encoded.npz'
NOTICE='Contributions to this model estimate'
LIMITATIONS=[
    'Contributions explain the frozen survey model estimate relative to the recorded training background; they are not personal causes or causal effects.',
    'The output is contemporaneous self-reported financial difficulty, not BNPL default or a validated future Australian outcome.',
    'Independent masking breaks dependencies between encoded inputs, including mutually exclusive one-hot categories. Summing by input preserves additivity but is not conditional/group-retrained SHAP.',
    'A different background can change the baseline and attribution allocation without changing the model probability.',
    'The existing model card records local probability overestimation, subgroup error differences, unweighted main evaluation and domain limits.',
]


def dense(array):
    return array.toarray() if hasattr(array,'toarray') else np.asarray(array)


def load_frozen():
    freeze=read_json('config/stage5_frozen.json')
    assert sha256(ROOT/freeze['artifact'])==freeze['artifact_sha256']
    assert sha256(ROOT/'config/feature_schema.json')==freeze['schema_sha256']
    assert sha256(ROOT/'data/splits/cfpb_split_ids.json')==freeze['split_sha256']
    model=joblib.load(ROOT/freeze['artifact'])
    assert model.classes_.tolist()==[0,1] and model['classifier'].coef_.shape[0]==1
    assert list(model['codebook'].schema)==freeze['features']
    return freeze,model


def encoded_mapping(model,features):
    pre=model['preprocessor'];name,category_pipe,columns=pre.transformers_[0]
    assert name=='categorical' and list(columns)==features
    encoder=category_pipe['onehot'];imputer=category_pipe['imputer']
    assert list(imputer.feature_names_in_)==features
    names=encoder.get_feature_names_out(features).tolist();mapping=[]
    for field,categories in zip(columns,encoder.categories_):
        mapping.extend([field]*len(categories))
    assert len(mapping)==len(names)==model['classifier'].coef_.shape[1]
    assert pre.get_feature_names_out().tolist()==['categorical__'+n for n in names]
    return names,mapping


def prepare_background(n=200,seed=20261105):
    freeze,model=load_frozen()
    if (ROOT/BACKGROUND_CONFIG).exists() or (ROOT/BACKGROUND_FILE).exists():raise FileExistsError('Background already prepared; reuse it instead of reselection')
    split=read_json('data/splits/cfpb_split_ids.json');raw_path=ROOT/'data/raw/cfpb/NFWBS_PUF_2016_data.csv'
    assert sha256(raw_path)==freeze['data_sha256']
    ids=np.random.default_rng(seed).choice(np.array(split['train']),size=min(n,len(split['train'])),replace=False).tolist()
    raw=pd.read_csv(raw_path).set_index('PUF_ID');x=raw.loc[ids,freeze['features']]
    encoded=dense(model[:-1].transform(x));path=ROOT/BACKGROUND_FILE;path.parent.mkdir(parents=True)
    np.savez_compressed(path,encoded=encoded)
    names,mapping=encoded_mapping(model,freeze['features'])
    write_json(BACKGROUND_CONFIG,{'method':'Uniform random rows without replacement from locked training IDs; fixed finite reference, not population representativeness','n':len(ids),'seed':seed,'ids':ids,
               'data_sha256':freeze['data_sha256'],'split_sha256':freeze['split_sha256'],'artifact_sha256':freeze['artifact_sha256'],'background_file':BACKGROUND_FILE,'background_sha256':sha256(path),
               'encoded_names':names,'encoded_to_raw':mapping,'space':'log-odds of class 1','method_name':'shap.LinearExplainer + shap.maskers.Independent','max_samples':len(ids),
               'background_mean_logit_not_mean_probability':True,'limitations':LIMITATIONS,
               'reference':'https://shap.readthedocs.io/en/latest/generated/shap.LinearExplainer.html'})
    return read_json(BACKGROUND_CONFIG)


class FrozenCFPBExplainer:
    """Load once per application session; prediction and local explanations only."""
    def __init__(self):
        import shap
        self.freeze,self.model=load_frozen();self.features=self.freeze['features'];self.schema=self.model['codebook'].schema
        self.background=read_json(BACKGROUND_CONFIG)
        assert self.background['artifact_sha256']==self.freeze['artifact_sha256']
        assert sha256(ROOT/self.background['background_file'])==self.background['background_sha256']
        split=read_json('data/splits/cfpb_split_ids.json');ids=self.background['ids']
        assert len(ids)==len(set(ids))==self.background['n'] and set(ids)<=set(split['train'])
        assert not set(ids)&(set(split['validation'])|set(split['test']))
        self.encoded_names,self.mapping=encoded_mapping(self.model,self.features)
        assert self.mapping==self.background['encoded_to_raw'] and self.encoded_names==self.background['encoded_names']
        bg=np.load(ROOT/self.background['background_file'])['encoded']
        self.explainer=shap.LinearExplainer(self.model['classifier'],shap.maskers.Independent(bg,max_samples=len(bg)))
        self.shap_version=shap.__version__

    def _frame(self,payload):
        if not isinstance(payload,dict) or set(payload)!=set(self.features):raise ValueError('Provide exactly the eight raw CFPB code fields; money is not survey coding')
        for k,v in payload.items():
            if v is not None and (isinstance(v,(bool,str)) or not isinstance(v,(int,float,np.integer,np.floating))):raise ValueError(f'{k}: numeric survey code or None required')
        return pd.DataFrame([payload],columns=self.features).astype(float)

    def explain(self,payload):
        x=self._frame(payload);encoded=dense(self.model[:-1].transform(x));explanation=self.explainer(encoded)
        values=np.asarray(explanation.values,dtype=float).reshape(1,-1)[0];base=float(np.asarray(explanation.base_values).reshape(-1)[0])
        logit=float(self.model.decision_function(x)[0]);prob=float(self.model.predict_proba(x)[0,list(self.model.classes_).index(1)])
        grouped={k:float(values[np.asarray(self.mapping)==k].sum()) for k in self.features}
        encoded_sum=float(values.sum());group_sum=float(sum(grouped.values()))
        errors={'encoded_additivity_absolute':abs(base+encoded_sum-logit),'raw_group_additivity_absolute':abs(base+group_sum-logit),
                'grouping_absolute':abs(group_sum-encoded_sum),'probability_absolute':abs(float(expit(base+group_sum))-prob)}
        if max(errors[k] for k in errors if k!='probability_absolute')>1e-10 or errors['probability_absolute']>1e-12:raise RuntimeError('SHAP reconstruction check failed; explanation withheld')
        cleaned=self.model['codebook'].transform(x);catpipe=self.model['preprocessor'].transformers_[0][1];effective=catpipe['imputer'].transform(cleaned)[0]
        rows=[]
        for i,k in enumerate(self.features):
            raw=x.iloc[0][k];is_missing=bool(pd.isna(cleaned.iloc[0][k]));labels=self.schema[k]['labels'];missing_labels=self.schema[k]['missing_codes']
            label='Missing (training-mode imputed)' if pd.isna(raw) else labels.get(str(int(raw)),missing_labels.get(str(int(raw)),'See codebook mapping'))
            rows.append({'feature':k,'label':self.schema[k]['question'],'raw_code':None if pd.isna(raw) else float(raw),'raw_label':label,'imputed':is_missing,'effective_encoded_category':float(effective[i]),
                         'contribution_log_odds':grouped[k],'contribution_display':f'{grouped[k]:+.4f} log-odds','direction':'increase' if grouped[k]>0 else 'decrease' if grouped[k]<0 else 'neutral'})
        return {'status':'ok','kind':'cfpb_frozen_lr_local_explanation','title':NOTICE,'label_meaning':'Self-reported difficulty covering expenses and paying all bills in a typical month (ENDSMEET codes 2/3 versus 1).',
                'positive_class':1,'probability':prob,'probability_display':f'{prob:.2%}','threshold':self.freeze['threshold'],'threshold_display':str(self.freeze['threshold']),
                'classification':int(prob>=self.freeze['threshold']),'classification_text':'Class 1 at the fixed reference threshold' if prob>=self.freeze['threshold'] else 'Class 0 at the fixed reference threshold',
                'decision_function':logit,'base_value_log_odds':base,'contribution_sum_log_odds':group_sum,'reconstructed_probability':float(expit(base+group_sum)),
                'contributions':rows,'encoded_contributions':[{'encoded_feature':n,'raw_feature':k,'contribution_log_odds':float(v)} for n,k,v in zip(self.encoded_names,self.mapping,values)],
                'checks':errors,'additivity_verified':True,'method':self.background['method_name'],'shap_version':self.shap_version,
                'artifact_sha256':self.freeze['artifact_sha256'],'background_sha256':self.background['background_sha256'],'background_n':self.background['n'],'space':'log-odds, not probability percentage points','limitations':LIMITATIONS}


def render_explanation(result,path,fictional=True):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'outputs/.mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=sorted(result['contributions'],key=lambda r:abs(r['contribution_log_odds']))
    fig,ax=plt.subplots(figsize=(9,5.2),layout='constrained');values=[r['contribution_log_odds'] for r in rows]
    bars=ax.barh([r['feature'] for r in rows],values,color=['#176b87' if v>=0 else '#c58223' for v in values])
    for bar,value in zip(bars,values):
        ax.text(value,bar.get_y()+bar.get_height()/2,f' {value:+.3f} ' ,ha='left' if value>=0 else 'right',va='center',fontsize=9)
    ax.axvline(0,color='#444444',lw=.8);ax.margins(x=.25);ax.spines[['top','right']].set_visible(False)
    ax.set(title=NOTICE,xlabel='Signed SHAP contribution (log-odds relative to training background)')
    fig.suptitle(f'Frozen CFPB LR | class-1 estimate {result["probability_display"]}')
    fig.supxlabel(('Fictional input | ' if fictional else '')+'Model attribution only; not personal causes or causal effects.',fontsize=9)
    fig.savefig(path,dpi=180);plt.close(fig)


def demo(output_dir='outputs/explanations/cfpb_shap_v1'):
    if not (ROOT/BACKGROUND_CONFIG).exists():prepare_background()
    out=ROOT/output_dir
    if out.exists():raise FileExistsError('Preserve completed explanations; choose a new --output-dir')
    out.mkdir(parents=True);explainer=FrozenCFPBExplainer();examples=read_json('data/metadata/extensions_baseline.json')['cfpb_inputs'];results=[]
    for i,payload in enumerate(examples):
        result=explainer.explain(payload);results.append(result);write_json(out/f'fictional_{i}.json',result)
        pd.DataFrame(result['contributions']).to_csv(out/f'fictional_{i}_contributions.csv',index=False)
        pd.DataFrame(result['encoded_contributions']).to_csv(out/f'fictional_{i}_encoded_contributions.csv',index=False)
    render_explanation(results[0],out/'fictional_local_contributions.png')
    # A second prespecified training-only background illustrates reference dependence, never model selection.
    ids=read_json('data/splits/cfpb_split_ids.json')['train'];other=np.random.default_rng(20261106).choice(ids,200,replace=False)
    raw=pd.read_csv(ROOT/'data/raw/cfpb/NFWBS_PUF_2016_data.csv').set_index('PUF_ID');other_x=dense(explainer.model[:-1].transform(raw.loc[other,explainer.features]))
    import shap
    other_explainer=shap.LinearExplainer(explainer.model['classifier'],shap.maskers.Independent(other_x,max_samples=200));x=explainer._frame(examples[0]);other_result=other_explainer(dense(explainer.model[:-1].transform(x)))
    original=results[0];second=np.asarray(other_result.values).reshape(-1);second_base=float(np.asarray(other_result.base_values).reshape(-1)[0])
    write_json(out/'background_sensitivity.json',{'policy':'Prespecified seed 20261106, 200 training rows; diagnostic only, primary background remains unchanged','ids':list(map(int,other)),
               'original_base_log_odds':original['base_value_log_odds'],'alternative_base_log_odds':second_base,'alternative_sum_plus_base':float(second_base+second.sum()),
               'unchanged_decision_function':original['decision_function'],'max_encoded_contribution_change':float(np.max(np.abs(second-np.array([r['contribution_log_odds'] for r in original['encoded_contributions']])))),
               'interpretation':'Reference changes attribution, not frozen-model output; no best-looking background selected'})
    write_json(out/'manifest.json',{'model_sha256':explainer.freeze['artifact_sha256'],'background_config_sha256':sha256(ROOT/BACKGROUND_CONFIG),
               'method':'Actual installed SHAP LinearExplainer; no model refit','max_reconstruction_errors':{k:max(r['checks'][k] for r in results) for k in results[0]['checks']},
               'files_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file()}})
    print('SHAP examples verified:',len(results),'max errors',read_json(out/'manifest.json')['max_reconstruction_errors'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',default='outputs/explanations/cfpb_shap_v1');a=p.parse_args();demo(a.output_dir)
