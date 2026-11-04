# Kaggle exploratory model card

Version exploratory_v1; completed 5 November 2026. Intended use: report appendix documenting classification of the recorded default_flag. No real-user credit decision or application-time/future default interpretation.

- Source: unchanged local 10,345 × 17 CSV; page screenshots mark CC0 1.0 Public Domain. Origin/synthesis, default standard/window and field timestamps remain unknown. Notebook code license is separate and unconfirmed; code was independently implemented.
- Frozen candidate: random_forest; threshold 0.5; no calibration; training only, fixed 6,207/2,069/2,069 split, seed 42. Parameters and artifact hashes: models/kaggle/exploratory_v1/frozen.json.
- Predictors: ten fields in config/kaggle_feature_schema.json. No identifiers, delay, misses, risk_score, customer_segment, their derivatives, date or target as inputs. Unknown credit/app/currency/DTI semantics remain limitations, not certified availability.
- Test AP 0.566320, AUC 0.697078, Brier 0.206394, Accuracy 0.644756, Precision 0.557662, Recall 0.436881, F1 0.489938. N=2,069, positives=808. Full comparators, validation and confidence intervals: kaggle_experiment.md.
- Large RF training/validation AP gap (~0.3922) indicates overfitting. Selection over LR was marginal and protocol-dependent. LR/RF test differences have paired intervals spanning zero; selection was not reopened.
- Calibration bins are descriptive and some are small. Brier does not certify calibration or real-world probability reliability. Bootstrap excludes full training/process and provenance uncertainty.
- No verified subgroup fairness, Australian validity, prospective validity, causal attribution, affordability or regulatory compliance. Country labels do not establish real samples; the twelve-month date gap prevents a continuous-market history claim.
- Dataset cannot validate CFPB, complement its labels or supply missing simulator expenses/savings. No joined records, averaged probabilities or comprehensive score.

**Display decision: 2 — report appendix only.** The application defaults to no Kaggle module. load_kaggle_research_summary(include_appendix=True) is an explicit research-results reader, never a personal prediction method. Reconsideration requires provenance/generator, label-window/maturity, timestamp and financial-unit evidence, not a favorable score.
