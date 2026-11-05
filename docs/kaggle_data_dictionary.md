# Kaggle BNPL field dictionary

> Current supplement (5 November 2026): user page screenshots mark CC0 1.0 Public Domain, and the preserved reference Notebook is now directly reviewed. See kaggle_notebook_review.md, kaggle_experiment.md and data_source_decision.md. The original audit below is retained as dated evidence; its license-unknown/defer-only status is superseded by this supplement, while its timing/semantic limits remain.

Checked 5 November 2026. Publisher definitions, units and as-of dates are not authenticated. Local distributions and numeric ranges are observations of the supplied CSV, not financial definitions. Full source qualification: kaggle_sources.md.

## user_id

Local facts: dtype=int64; min=1, max=10345; unique=10345; standard missing=0.

Meaning evidence: Local integer identifiers, unique and ordered 1..10345; real identity and semantic grain unverified

Unit: Identifier

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Key/quality checks only; never predictor

Simulator mapping: No automatic mapping

## age

Local facts: dtype=int64; min=18, max=59; unique=42; standard missing=0.

Meaning evidence: Name suggests age; observed 18..59. No publisher codebook obtained

Unit: Years suggested by name; unverified

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Local descriptive profile; not a predictive endorsement

Simulator mapping: No automatic mapping

## employment_type

Local facts: Recorded categories: Salaried (2632); Unemployed (2632); Self-Employed (2550); Student (2531).

Meaning evidence: Four recorded categories; no sampling/employment definition

Unit: Category

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: File-level category audit only

Simulator mapping: No automatic mapping

## monthly_income

Local facts: dtype=float64; min=5000, max=145767; unique=9984; standard missing=0.

Meaning evidence: Column name suggests monthly income; tax basis, person/household scope and reporting period unverified

Unit: Currency and common numeraire unknown; month only suggested by name

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Raw range profile only; no country amount-mean comparisons

Simulator mapping: Do not autofill I: tax/currency/period semantics unresolved

## credit_score

Local facts: dtype=int64; min=300, max=850; unique=534; standard missing=0.

Meaning evidence: Observed 300..850; provider, country comparability and score date unknown

Unit: Recorded score units; not authenticated as FICO

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Descriptive audit only

Simulator mapping: No automatic mapping

## purchase_amount

Local facts: dtype=float64; min=100, max=5000; unique=4011; standard missing=0.

Meaning evidence: Observed 100..5000; financed principal versus total price unknown

Unit: Currency unknown; not verified comparable across countries

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Boundary/range check only

Simulator mapping: Cannot divide by instalment count and call it monthly Bnew

## product_category

Local facts: Recorded categories: Fashion (2166); Electronics (2085); Beauty (2072); Home (2052); Sports (1970).

Meaning evidence: Five observed category strings

Unit: Category

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Auxiliary local EDA, not real-market shares

Simulator mapping: No automatic mapping

## bnpl_installments

Local facts: dtype=int64; min=3, max=12; unique=4; standard missing=0.

Meaning evidence: Recorded values3/6/9/12; total/remaining/paid count unknown

Unit: Count/code suggested; frequency and timing unknown

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Recorded-value frequency plot only

Simulator mapping: No monthly-payment mapping without schedule, fees and first-payment assumptions

## repayment_delay_days

Local facts: dtype=int64; min=0, max=33; unique=33; standard missing=0.

Meaning evidence: Integer 0..33; days suggested by name; current versus historical obligation unknown

Unit: Days by field name; aggregation/window/grace period unknown

Time availability: Repayment-related state; no dated historical evidence before the application

Recommended use: Exclude application-time prediction; descriptive audit only

Simulator mapping: No automatic mapping

## missed_payments

Local facts: dtype=int64; min=0, max=7; unique=8; standard missing=0.

Meaning evidence: Integer 0..7; event/count and observation period undefined

Unit: Payment count suggested; event definition unknown

Time availability: Repayment-related state; no dated pre-application history

Recommended use: Exclude application-time prediction; descriptive audit only

Simulator mapping: No automatic mapping

## default_flag

Local facts: dtype=int64; min=0, max=1; unique=2; standard missing=0.

Meaning evidence: Binary0/1 locally verified; default criterion, reference obligation and window unknown

Unit: Recorded binary flag, not validated loan-default outcome

Time availability: Outcome/as-of date and maturity/censoring unknown

Recommended use: Report flag distribution only; not a qualified predictive target

Simulator mapping: No automatic mapping

## app_usage_frequency

Local facts: dtype=float64; min=1, max=10; unique=901; standard missing=0.

Meaning evidence: Observed numeric1..10 with decimals; visits versus index and time period unknown

Unit: Unknown

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Descriptive range only

Simulator mapping: No automatic mapping

## location

Local facts: Recorded categories: Germany (1760); Canada (1740); USA (1736); India (1723); Australia (1722); UK (1664).

Meaning evidence: Six observed country-name labels; residence/merchant jurisdiction unclear

Unit: Category; does not establish currency

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: File category count only; do not compare monetary means across countries

Simulator mapping: No automatic mapping

## transaction_date

Local facts: Recorded categories: ISO-formatted strings; see date coverage audit.

Meaning evidence: ISO dates parse; onlyJan-Jun 2023 andJul-Dec 2024 have records

Unit: Calendar date; event identity/sampling unknown

Time availability: No application/outcome/follow-up timestamps

Recommended use: Coverage audit only, not market trend or automatic temporal split

Simulator mapping: No automatic mapping

## debt_to_income_ratio

Local facts: dtype=float64; min=0.000811416, max=0.72346; unique=10327; standard missing=0.

Meaning evidence: Every local row matches purchase_amount/monthly_income within 1e-8; authenticated generator unknown

Unit: Ratio of recorded numeric fields; currency/time basis unverified; not established as a dimensionless debt-service ratio

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Audit diagnostic only; not conventional household DTI

Simulator mapping: Do not infer D from this ratio; non-BNPL monthly debt payments absent

## risk_score

Local facts: dtype=float64; min=0, max=398; unique=876; standard missing=0.

Meaning evidence: Every local row matches 0.4*(850-credit_score)+2*delay+20*misses within 1e-8; not publisher-confirmed generation code

Unit: Recorded score units; no probability or approved risk scale

Time availability: Inherits unresolved timing of delay/missed-payment fields

Recommended use: Exclude application-time model; document arithmetic dependency

Simulator mapping: No automatic mapping

## customer_segment

Local facts: Recorded categories: High Risk (7569); Medium Risk (2200); Low Risk (576).

Meaning evidence: High/Medium/Low Risk strings observed; generation thresholds not authenticated

Unit: Unvalidated category labels

Time availability: No publisher-verified definition or as-of timestamp obtained

Recommended use: Descriptive crosstab only; not validated risk bands

Simulator mapping: No automatic mapping

## Missing-value and anomaly policy

No standard missing values or blank strings were found. No publisher special-missing codes were obtained. Candidate999/9999 tokens occur as sequential IDs and are not recoded. Numeric zeros, minima and maxima remain unchanged. IQR flags are descriptive screens, not validated errors; no row is removed or corrected.
