"""Validation-only metrics for stage three; no test data reader."""
import numpy as np
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix)

def metrics(y, probabilities, threshold=0.5, weights=None):
    y=np.asarray(y); p=np.asarray(probabilities)
    if not np.isfinite(p).all() or ((p<0)|(p>1)).any():
        raise ValueError('Invalid predicted probabilities')
    pred=p>=threshold
    kw={'sample_weight':weights}
    has_positive=bool(pred.any())
    return {'n':len(y),'positive_rate':float(np.average(y,weights=weights)),
        'threshold':threshold,'accuracy':float(accuracy_score(y,pred,**kw)),
        'precision':float(precision_score(y,pred,zero_division=0,**kw)) if has_positive else None,
        'precision_note':None if has_positive else 'N/A: no predicted positives',
        'recall':float(recall_score(y,pred,zero_division=0,**kw)),
        'f1':float(f1_score(y,pred,zero_division=0,**kw)),
        'roc_auc':float(roc_auc_score(y,p,**kw)),
        'average_precision':float(average_precision_score(y,p,**kw)),
        'brier':float(brier_score_loss(y,p,**kw)),
        'confusion_matrix_tn_fp_fn_tp':confusion_matrix(y,pred,labels=[0,1],**kw).ravel().tolist()}
