"""Fixed-model metrics and paired respondent bootstrap with explicit N/A rules."""
import numpy as np

CI_METRICS = ['positive_rate','accuracy','precision','recall','f1','roc_auc','average_precision','brier','false_positive_rate']


def binary_metrics(y, probability, threshold=0.5, weights=None):
    y=np.asarray(y); p=np.asarray(probability,dtype=float)
    if y.ndim!=1 or p.shape!=y.shape or not len(y): raise ValueError('Nonempty equal-length vectors required')
    if not np.isin(y,[0,1]).all() or not np.isfinite(p).all() or ((p<0)|(p>1)).any(): raise ValueError('Invalid binary labels or probabilities')
    w=np.ones(len(y)) if weights is None else np.asarray(weights,dtype=float)
    if w.shape!=y.shape or not np.isfinite(w).all() or (w<=0).any(): raise ValueError('Weights must be finite and positive')
    pred=p>=threshold; yes=y==1; no=~yes
    tp=float(w[yes&pred].sum()); fp=float(w[no&pred].sum()); fn=float(w[yes&~pred].sum()); tn=float(w[no&~pred].sum())
    pos=tp+fn; neg=tn+fp; total=pos+neg
    divide=lambda a,b: float(a/b) if b else None
    order=np.argsort(-p,kind='stable'); ps=p[order]; ys=y[order]; ws=w[order]
    ends=np.r_[np.flatnonzero(np.diff(ps)),len(p)-1]
    tps=np.cumsum(ws*ys)[ends]; fps=np.cumsum(ws*(1-ys))[ends]
    ap=float(np.sum(np.diff(np.r_[0,tps])/pos*(tps/(tps+fps)))) if pos else None
    auc=float(np.trapezoid(np.r_[0,tps]/pos,np.r_[0,fps]/neg)) if pos and neg else None
    notes={}
    if not pos: notes.update(recall='No positive outcomes',average_precision='No positive outcomes')
    if not neg: notes['false_positive_rate']='No negative outcomes'
    if not pos or not neg: notes['roc_auc']='Both outcome classes required'
    if not tp+fp: notes['precision']='No predicted positives'
    if not 2*tp+fp+fn: notes['f1']='No actual or predicted positives'
    return {'n':len(y),'positive_n':int(yes.sum()),'negative_n':int(no.sum()),'positive_rate':pos/total,
            'threshold':threshold,'accuracy':(tp+tn)/total,'precision':divide(tp,tp+fp),'recall':divide(tp,pos),
            'f1':divide(2*tp,2*tp+fp+fn),'false_positive_rate':divide(fp,neg),'roc_auc':auc,'average_precision':ap,
            'brier':float(np.average((p-y)**2,weights=w)),
            'confusion_matrix_tn_fp_fn_tp':[tn,fp,fn,tp],
            'confusion_unit':'respondents' if weights is None else 'sum of finalwt', 'na_reasons':notes}


def interval(values, minimum_valid_fraction=0.9):
    a=np.asarray(values,dtype=float); finite=a[np.isfinite(a)]
    sufficient=bool(len(a) and len(finite)/len(a)>=minimum_valid_fraction)
    return {'lower':float(np.quantile(finite,.025)) if sufficient else None,
            'upper':float(np.quantile(finite,.975)) if sufficient else None,
            'valid_replicates':len(finite),'invalid_replicates':len(a)-len(finite),
            'reason':None if sufficient else 'Insufficient defined replicates; see point-estimate N/A reason'}


def paired_bootstrap(y, predictions, replicates, seed, threshold=0.5, minimum_valid_fraction=.9):
    """The same unstratified row draw is used for every model in each replicate."""
    y=np.asarray(y); rng=np.random.default_rng(seed)
    indices=rng.integers(0,len(y),size=(replicates,len(y)),dtype=np.int32)
    draws={name:{k:np.full(replicates,np.nan) for k in CI_METRICS} for name in predictions}
    for b,idx in enumerate(indices):
        for name,p in predictions.items():
            r=binary_metrics(y[idx],np.asarray(p)[idx],threshold)
            for key in CI_METRICS:
                if r[key] is not None: draws[name][key][b]=r[key]
    intervals={n:{k:interval(v,minimum_valid_fraction) for k,v in ds.items()} for n,ds in draws.items()}
    paired={}
    if 'logistic_regression' in draws:
        for comparator in ['dummy','random_forest']:
            if comparator in draws:
                paired[comparator]={k:interval(draws['logistic_regression'][k]-draws[comparator][k],minimum_valid_fraction) for k in ['average_precision','roc_auc','brier']}
    return intervals,paired,draws,indices


def wilson_interval(successes,n):
    if n==0:return None,None
    z=1.959963984540054; q=successes/n; den=1+z*z/n
    center=(q+z*z/(2*n))/den; half=z*np.sqrt(q*(1-q)/n+z*z/(4*n*n))/den
    return max(0,float(center-half)),min(1,float(center+half))


def calibration_bins(y,p,bins=10,small_n=30):
    y=np.asarray(y);p=np.asarray(p);edges=np.arange(bins+1)/bins
    idx=np.clip(np.searchsorted(edges,p,side='right')-1,0,bins-1)
    rows=[]
    for i in range(bins):
        mask=idx==i; n=int(mask.sum()); count=int(y[mask].sum()); lo,hi=wilson_interval(count,n)
        rows.append({'bin':i,'lower_edge':float(edges[i]),'upper_edge':float(edges[i+1]),'n':n,'positive_n':count,
                     'mean_prediction':float(p[mask].mean()) if n else None,'observed_rate':count/n if n else None,
                     'observed_wilson_lower':lo,'observed_wilson_upper':hi,'small_bin':n<small_n})
    return rows
