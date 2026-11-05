"""Audit accounting and conservative interpretation checks, without model fitting."""
import numpy as np
import pandas as pd
from src.kaggle_audit import quality_profile,date_profile,identity_checks,verify
from src.common import ROOT,read_json


def test_missing_ids_duplicates_and_sentinels_are_reported_not_rewritten():
    frame=pd.DataFrame({'user_id':[1,1,np.nan],'measurement':[0,-1,999]})
    original=frame.copy(deep=True)
    profile,summary=quality_profile(frame)
    assert summary['missing_user_id_n']==1
    assert summary['duplicate_user_id_extra_rows']==1
    assert summary['rows_with_duplicated_nonmissing_id']==2
    assert profile.set_index('field').loc['measurement','negative_n']==1
    pd.testing.assert_frame_equal(frame,original)


def test_dates_retain_parse_failure_and_explicit_coverage_gap():
    values=pd.Series(['2023-01-01','invalid','2023-03-01',None])
    parsed,summary,months=date_profile(values)
    assert summary['nonmissing_parse_failures']==1
    assert summary['zero_record_months']==['2023-02']
    assert int(months.sum())==2 and parsed.isna().sum()==2


def test_algebraic_check_reports_residual_not_authenticated_generation():
    frame=pd.DataFrame({'purchase_amount':[100.,200.],'monthly_income':[1000.,1000.],
                        'debt_to_income_ratio':[.1,.21],'credit_score':[500,600],
                        'repayment_delay_days':[1,2],'missed_payments':[0,1],
                        'risk_score':[142.,124.]})
    out=identity_checks(frame).set_index('field')
    assert out.loc['debt_to_income_ratio','matches_at_1e_8_n']==1
    assert out.loc['risk_score','matches_at_1e_8_n']==2
    assert 'not publisher-confirmed' in out.loc['risk_score','evidence']


def test_saved_audit_counts_reconcile():
    out=ROOT/'outputs/kaggle_audit/v1';summary=read_json(out/'quality_summary.json')
    assert summary['model_training_performed'] is False
    categories=pd.read_csv(out/'category_distributions.csv')
    for _,group in categories.groupby('field'):assert group.n.sum()==summary['rows']
    counts=pd.read_csv(out/'monthly_record_counts.csv');assert counts.records.sum()==summary['rows']
    assert len(counts[counts.records==0])==12
    identities=pd.read_csv(out/'algebraic_consistency_checks.csv')
    assert (identities.checked_n==summary['rows']).all()
    assert (identities.matches_at_1e_8_n==summary['rows']).all()
    review=pd.read_csv(out/'field_leakage_review.csv')
    assert len(review[~review.field.str.startswith('Notebook:')])==summary['columns']
