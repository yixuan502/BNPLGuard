"""Local-only BNPL source audit and bounded descriptive EDA; never train a model."""
import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import numpy as np
import pandas as pd
from .common import ROOT, read_json, write_json, sha256

DATA='data/raw/kaggle_bnpl/Buy_Now_Pay_Later_BNPL_CreditRisk_Dataset.csv'
SENTINELS={'','unknown','unk','na','n/a','none','null','missing','not available','-1','999','9999'}


def quality_profile(frame):
    """Report, never replace, possible sentinels and boundary concentrations."""
    rows=[]
    for name in frame:
        s=frame[name];text=s.astype('string').str.strip().str.lower()
        numeric=pd.api.types.is_numeric_dtype(s)
        row={'field':name,'dtype':str(s.dtype),'n':len(s),'standard_missing_n':int(s.isna().sum()),
             'distinct_nonmissing_n':int(s.nunique()),'blank_n':int(text.eq('').sum()),
             'possible_sentinel_n':int(text.isin(SENTINELS).sum()),'sentinel_policy':'candidate only; no recoding without source definitions'}
        if numeric:
            v=s.dropna();finite=v[np.isfinite(v)]
            q1,q3=finite.quantile([.25,.75]);iqr=q3-q1
            row.update(min=float(finite.min()),max=float(finite.max()),median=float(finite.median()),
                       q01=float(finite.quantile(.01)),q25=float(q1),q75=float(q3),q99=float(finite.quantile(.99)),
                       nonfinite_n=int((~np.isfinite(v)).sum()),negative_n=int((v<0).sum()),zero_n=int((v==0).sum()),
                       min_n=int((s==finite.min()).sum()),max_n=int((s==finite.max()).sum()),
                       iqr_flag_n=int(((finite<q1-1.5*iqr)|(finite>q3+1.5*iqr)).sum()))
        rows.append(row)
    ids=frame['user_id']
    summary={'rows':len(frame),'columns':len(frame.columns),'standard_missing_total':int(frame.isna().sum().sum()),
             'exact_duplicate_rows':int(frame.duplicated().sum()),'missing_user_id_n':int(ids.isna().sum()),
             'duplicate_user_id_extra_rows':int(ids.dropna().duplicated().sum()),
             'rows_with_duplicated_nonmissing_id':int((ids.notna()&ids.duplicated(keep=False)).sum()),
             'distinct_nonmissing_user_ids':int(ids.nunique()),
             'observed_grain':'One row per nonmissing user_id in this file' if not ids.isna().any() and not ids.duplicated().any() else 'Repeated or missing user IDs; inspect counts',
             'semantic_grain':'Unknown: identifier uniqueness does not authenticate people, accounts or transactions.'}
    return pd.DataFrame(rows),summary


def date_profile(values):
    parsed=pd.to_datetime(values,format='%Y-%m-%d',errors='coerce')
    valid=parsed.dropna()
    full=pd.period_range(valid.min().to_period('M'),valid.max().to_period('M'),freq='M') if len(valid) else []
    counts=valid.dt.to_period('M').value_counts().reindex(full,fill_value=0).sort_index()
    return parsed,{'valid_dates':int(parsed.notna().sum()),'nonmissing_parse_failures':int((values.notna()&parsed.isna()).sum()),
                   'first_date':valid.min().date().isoformat() if len(valid) else None,
                   'last_date':valid.max().date().isoformat() if len(valid) else None,
                   'distinct_dates':int(valid.nunique()),'zero_record_months':[str(k) for k,v in counts.items() if v==0],
                   'interpretation':'Recorded dates only; application/outcome/as-of dates and sampling process are unknown.'},counts


def identity_checks(frame):
    """Exploratory algebraic equalities, not authenticated data-generation rules."""
    candidates={
        'debt_to_income_ratio':('purchase_amount / monthly_income',frame.purchase_amount/frame.monthly_income),
        'risk_score':('0.4 * (850 - credit_score) + 2 * repayment_delay_days + 20 * missed_payments',.4*(850-frame.credit_score)+2*frame.repayment_delay_days+20*frame.missed_payments)}
    rows=[]
    for name,(expression,predicted) in candidates.items():
        mask=np.isfinite(frame[name])&np.isfinite(predicted);error=(frame.loc[mask,name]-predicted[mask]).abs()
        rows.append({'field':name,'candidate_expression':expression,'checked_n':int(mask.sum()),'matches_at_1e_8_n':int((error<=1e-8).sum()),
                     'max_absolute_residual':float(error.max()) if len(error) else None,
                     'evidence':'Direct arithmetic consistency in local file; not publisher-confirmed generation code or target causality.'})
    return pd.DataFrame(rows)


def label_groups(frame):
    groupings={
        'repayment_delay_days':pd.cut(frame.repayment_delay_days,[-np.inf,0,7,14,np.inf],labels=['0 or below','1-7','8-14','15+']),
        'missed_payments':pd.cut(frame.missed_payments,[-np.inf,0,1,2,np.inf],labels=['0 or below','1','2','3+']),
        'risk_score':pd.cut(frame.risk_score,[-np.inf,100,200,300,np.inf],right=False,labels=['Below 100','100-199.999','200-299.999','300+']),
        'debt_to_income_ratio':pd.cut(frame.debt_to_income_ratio,[-np.inf,.1,.2,.4,np.inf],right=False,labels=['Below .1','.1-.1999','.2-.3999','.4+']),
        'customer_segment':frame.customer_segment}
    rows=[]
    for field,groups in groupings.items():
        groups=groups.astype('string').fillna('Missing/unbinned')
        for label in groups.unique():
            group=frame.loc[groups==label];valid=group.default_flag.isin([0,1]);yes=int((group.default_flag==1).sum());no=int((group.default_flag==0).sum())
            rows.append({'field':field,'group':label,'n':len(group),'flag_0_n':no,'flag_1_n':yes,
                         'invalid_or_missing_flag_n':int((~valid).sum()),'recorded_flag_1_share':yes/(yes+no) if yes+no else None,
                         'mixed_flag_values':bool(yes and no),'small_group':len(group)<30,
                         'meaning':'Exploratory co-occurrence; bins are not clinical/regulatory/industry thresholds.'})
    return pd.DataFrame(rows)


def audit(output_dir='outputs/kaggle_audit/v1'):
    out=ROOT/output_dir
    if out.exists():raise FileExistsError(f'Preserve {out}; choose a new --output-dir or use --verify-only.')
    out.mkdir(parents=True);data_path=ROOT/DATA;original_hash=sha256(data_path)
    # Raw strings detect tokens that pandas may already interpret as ordinary NA.
    raw_text=pd.read_csv(data_path,dtype='string',keep_default_na=False)
    frame=pd.read_csv(data_path)
    profile,summary=quality_profile(frame)
    profile['raw_token_sentinel_n']=[int(raw_text[c].str.strip().str.lower().isin(SENTINELS).sum()) for c in profile.field]
    profile.to_csv(out/'column_quality.csv',index=False)
    summary.update({'sha256':original_hash,'bytes':data_path.stat().st_size,'source_path':DATA,'checked_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),
                    'id_min':int(frame.user_id.min()),'id_max':int(frame.user_id.max()),'id_is_ordered_1_to_n':bool(np.array_equal(frame.user_id,np.arange(1,len(frame)+1))),
                    'recorded_flag_counts':{str(k):int(v) for k,v in frame.default_flag.value_counts(dropna=False).items()},
                    'recorded_flag_1_share':float((frame.default_flag==1).mean()),'default_definition':'Unknown; no verified criterion or outcome window.',
                    'provenance':'unverified; exact-URL-linked third-party synthetic claim exists, primary card inaccessible',
                    'synthetic_status':'not authenticated by primary evidence','model_training_performed':False})
    parsed,dates,month_counts=date_profile(frame.transaction_date);summary['dates']=dates
    month_counts.rename_axis('month').rename('records').to_csv(out/'monthly_record_counts.csv')
    frame.user_id.value_counts(dropna=False).sort_index().rename_axis('user_id').rename('records').to_csv(out/'records_per_user.csv')
    frame.user_id.value_counts(dropna=False).value_counts().sort_index().rename_axis('records_per_user').rename('users').to_csv(out/'user_multiplicity_distribution.csv')
    categories=[]
    for field in ['employment_type','product_category','bnpl_installments','default_flag','location','customer_segment']:
        for value,count in frame[field].value_counts(dropna=False).items():
            categories.append({'field':field,'value':str(value),'n':int(count),'share':float(count/len(frame))})
    pd.DataFrame(categories).to_csv(out/'category_distributions.csv',index=False)
    identity_checks(frame).to_csv(out/'algebraic_consistency_checks.csv',index=False)
    label_groups(frame).to_csv(out/'label_cooccurrence.csv',index=False)
    cases={
        'flag_1_with_zero_recorded_delay_and_misses':int(((frame.default_flag==1)&(frame.repayment_delay_days==0)&(frame.missed_payments==0)).sum()),
        'flag_0_with_any_recorded_delay':int(((frame.default_flag==0)&(frame.repayment_delay_days>0)).sum()),
        'flag_0_with_any_missed_payment':int(((frame.default_flag==0)&(frame.missed_payments>0)).sum()),
        'purchase_amount_at_5000':int((frame.purchase_amount==5000).sum()),
        'credit_score_at_300':int((frame.credit_score==300).sum()),
        'numeric_noninteger_bnpl_installments':int((frame.bnpl_installments%1!=0).sum()),
        'numeric_noninteger_delay_or_missed_count':int(((frame.repayment_delay_days%1!=0)|(frame.missed_payments%1!=0)).sum()),
        'negative_recorded_numeric_values':int((frame.select_dtypes(include='number')<0).sum().sum())}
    summary['diagnostic_counts']=cases
    summary['cautions']='Zero or boundary values are not recoded as missing. Outlier flags and caps do not prove synthesis. Date gaps do not identify a market trend.'
    write_json(out/'quality_summary.json',summary)
    sources=ROOT/'data/metadata/kaggle_sources'
    for name in ['evidence.json','access_log.json']:
        if (sources/name).exists():(out/name).write_bytes((sources/name).read_bytes())
    write_json(out/'audit_config.json',{'raw_unchanged':True,'fit_models':False,'date_parser':'strict YYYY-MM-DD','iqr_rule':'Q1-1.5IQR or Q3+1.5IQR; descriptive only','arithmetic_tolerance':1e-8,
               'sentinel_candidates':sorted(SENTINELS),'sentinel_policy':'Report only; semantics unknown','chart_units':'record counts and recorded values; no currency comparisons',
               'label_groups':'Predefined diagnostic bins in label_groups; no threshold optimization or classifier fitting','source_refresh':'not automatic; stored access records/evidence reused'})
    review_path=ROOT/'data/metadata/kaggle_field_review.json'
    if review_path.exists():
        review=read_json(review_path)
        pd.DataFrame(review['fields']).to_csv(out/'field_leakage_review.csv',index=False)
        write_json(out/'field_review_evidence.json',review)
    render_figures(out,frame,month_counts)
    assert sha256(data_path)==original_hash
    protected=read_json('data/metadata/kaggle_audit_protected_before.json')
    assert all(sha256(ROOT/p)==h for p,h in protected.items())
    write_json(out/'manifest.json',{'completed_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat(),'data_sha256':original_hash,'source_sha256':sha256(Path(__file__)),
               'protected_existing_files':len(protected),'protected_snapshot_sha256':sha256(ROOT/'data/metadata/kaggle_audit_protected_before.json'),
               'all_protected_files_unchanged':True,'no_model_training':True,'field_review_sha256':sha256(review_path) if review_path.exists() else None,'source_evidence_sha256':{p.name:sha256(p) for p in sources.iterdir() if p.is_file()},'output_sha256':{p.name:sha256(p) for p in out.iterdir() if p.is_file()}})
    print(f'Local audit complete: {frame.shape[0]} rows x {frame.shape[1]} columns; no training. {out}')
    return summary


def render_figures(out,frame,months):
    os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'outputs/.mplconfig'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    footer=f'Local CSV | n = {len(frame):,} records | Provenance unverified; synthesis claimed by a third party, not authenticated.'
    fig,axes=plt.subplots(1,3,figsize=(12,4.2),layout='constrained')
    for ax,field,title in zip(axes,['bnpl_installments','product_category','default_flag'],['Recorded instalment field','Recorded product categories','Recorded binary flag']):
        counts=frame[field].value_counts().sort_index()
        bars=ax.bar([str(v) for v in counts.index],counts.to_numpy(),color='#126b77')
        ax.bar_label(bars,labels=[f'{n:,}' for n in counts],padding=3,fontsize=9)
        ax.set_ylim(0,max(counts)*1.18);ax.set_ylabel('Records');ax.set_title(title,fontsize=11)
        ax.set_xlabel('Count/code; frequency unknown' if field=='bnpl_installments' else field)
        if field=='product_category':ax.tick_params(axis='x',labelrotation=35,labelsize=8)
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.suptitle('Kaggle-file descriptive audit | not real-market estimates',fontsize=13)
    fig.supxlabel(footer,fontsize=9);fig.savefig(out/'record_distributions.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,4),layout='constrained')
    ax.bar(range(len(months)),months.to_numpy(),color='#126b77')
    ax.set_xticks(range(len(months)),[str(v) for v in months.index],rotation=55,ha='right',fontsize=8)
    ax.set(ylabel='Recorded rows per month',xlabel='Recorded transaction_date month (event meaning unverified)',title='File coverage gap | zero bars mean no rows, not no market activity')
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    fig.supxlabel(footer,fontsize=9);fig.savefig(out/'recorded_date_coverage.png',dpi=180);plt.close(fig)


def verify(directory):
    out=ROOT/directory;m=read_json(out/'manifest.json')
    assert sha256(ROOT/DATA)==m['data_sha256']
    assert sha256(Path(__file__))==m['source_sha256']
    if m.get('field_review_sha256'):assert sha256(ROOT/'data/metadata/kaggle_field_review.json')==m['field_review_sha256']
    for name,h in m['output_sha256'].items():assert sha256(out/name)==h,name
    for rel,h in read_json('data/metadata/kaggle_audit_protected_before.json').items():assert sha256(ROOT/rel)==h,rel
    print('PASS: raw file, audit outputs and all prior frozen/simulator files unchanged.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output-dir',default='outputs/kaggle_audit/v1');p.add_argument('--verify-only',action='store_true');args=p.parse_args()
    if args.verify_only:verify(args.output_dir)
    else:audit(args.output_dir)
