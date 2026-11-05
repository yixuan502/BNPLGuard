# Kaggle label and leakage review

> Current supplement (5 November 2026): user page screenshots mark CC0 1.0 Public Domain, and the preserved reference Notebook is now directly reviewed. See kaggle_notebook_review.md, kaggle_experiment.md and data_source_decision.md. The original audit below is retained as dated evidence; its license-unknown/defer-only status is superseded by this supplement, while its timing/semantic limits remain.

No model was trained. These are eligibility/meaning checks, not a competition for the best predictor. The complete21-row field/derived-variable review is saved as outputs/kaggle_audit/v1/field_leakage_review.csv; the raw17-field dictionary is in kaggle_data_dictionary.md.

| Field | Meaning evidence | Time availability | Relation to label | Potential leakage | Suggested use |
|---|---|---|---|---|---|
| repayment_delay_days | Integer 0..33; days suggested by name; current versus historical obligation unknown | Repayment-related state; no dated historical evidence before the application | Both flag classes appear across recorded delay ranges | High if post-origination/current obligation; not eligible for application-time features without historical proof | Exclude application-time prediction; descriptive audit only |
| missed_payments | Integer 0..7; event/count and observation period undefined | Repayment-related state; no dated pre-application history | Flag 0 and 1 coexist for most recorded counts; high-count cells can be tiny | High if current/post-origination outcome; history cannot be assumed | Exclude application-time prediction; descriptive audit only |
| debt_to_income_ratio | Every local row matches purchase_amount/monthly_income within 1e-8; authenticated generator unknown | No publisher-verified definition or as-of timestamp obtained | Redundant with its two component fields; no direct target transform established | Semantic misuse and redundancy; label leakage not demonstrated by this equality | Audit diagnostic only; not conventional household DTI |
| risk_score | Every local row matches 0.4*(850-credit_score)+2*delay+20*misses within 1e-8; not publisher-confirmed generation code | Inherits unresolved timing of delay/missed-payment fields | Association and overlapping flag ranges; no proof default_flag generated from it | High: algebraically incorporates repayment-related states; do not assume available at application | Exclude application-time model; document arithmetic dependency |
| customer_segment | High/Medium/Low Risk strings observed; generation thresholds not authenticated | No publisher-verified definition or as-of timestamp obtained | All three groups contain both binary flags; not deterministic default mapping | Potential same-rule score/category proxy; target derivation and timing unresolved | Descriptive crosstab only; not validated risk bands |
| Notebook: income_per_installment | Historical 2026-11-04 local Notebook read in this chat; source bytes absent now and correspondence to supplied online Notebook unverified; expression monthly_income/(bnpl_installments+1) | Inherits income/count timing gaps | No independently verified predictive meaning | Undefined denominator convention; semantic misuse; full-data imputation would also leak preprocessing if copied | Conditional method warning only; not newly verified online code |
| Notebook: delay_ratio | Historical 2026-11-04 local Notebook read in this chat; source bytes absent now and correspondence to supplied online Notebook unverified; expression repayment_delay_days/(bnpl_installments+1) | Inherits unresolved repayment-outcome timing | No authenticated label-generation role | High: transforms potentially post-outcome delay; denominator does not remove leakage | Exclude application-time feature; conditional review only |
| Notebook: month | Historical 2026-11-04 local Notebook read in this chat; source bytes absent now and correspondence to supplied online Notebook unverified; calendar month from transaction_date | Date meaning and coverage gap remain unresolved | No future label window established | Calendar feature does not repair missing prospective design | Coverage EDA only; conditional review, not current online-version certification |
| Notebook: other derived variables | Current requested Notebook cells/version could not be retrieved | Unknown | Unknown | Cannot certify unseen feature engineering or preprocessing | Do not adopt unaudited code; original Notebook/version/license needed for a complete code audit |

## Historical versus current repayment information

No field has timestamped evidence establishing pre-application history. The observed delay/miss variables could concern the current transaction, past transactions, an aggregated state or a constructed record. They cannot be approved as historical application-time features merely because their names are familiar. Authentic dated prior behavior would require a preceding observation window and an application cutoff; current/post-origination outcomes must be excluded from application-time prediction. Such evidence was not obtained.

The local risk_score exactly incorporates delay and missed-payment fields in an exploratory arithmetic check. Even without proof of label derivation, it carries their timing risk. customer_segment has no authenticated generation rule; it must not be assumed independent of the score, label or shared construction rules. DTI is different: its observed identity with purchase/income establishes redundancy and semantic concerns, not target leakage by itself. No default_flag-based score formula is claimed.

## Local arithmetic and label co-occurrence

All 10345 rows match, to absolute tolerance1e-8:

```
debt_to_income_ratio = purchase_amount / monthly_income
risk_score = 0.4*(850-credit_score) + 2*repayment_delay_days + 20*missed_payments
```

These are **exploratory equalities in this file**, not authenticated publisher generation code, proof of causality, or evidence that default_flag was generated by either expression. Residual maxima are below 1e-16 for the ratio and 2.85e-14 for the score. With income frequency/currency unverified, the purchase/income ratio cannot be labeled a conventional dimensionless monthly debt-service ratio. Necessary debt repayment amounts are absent.

Every inspected delay/miss/score/DTI diagnostic bin and each segment contains both binary flags. The score ranges for flags 0/1 overlap. There are 325 records with flag 1 despite zero recorded delay and zero missed payments. This does not prove incorrect labels: future windows, definitions or construction could explain it, but none is documented. Records are preserved rather than deleted to manufacture deterministic labels. The flag 1 share rises across some diagnostic groups; that is local association, not a verified rule or prospective capability.

A calendar transaction_date without application/outcome timestamps cannot establish label maturity or a valid future-prediction split. The 12-month coverage gap further prevents treating this file as continuous market history. No random or temporal model split was created in this audit.

The requested online Notebook was inaccessible. Only three historically inspected local expressions received conditional review; unseen/current derivatives remain unknown. None was adopted or executed. Current source/version/license and full preprocessing/splitting code would be necessary to complete a Notebook implementation audit.
