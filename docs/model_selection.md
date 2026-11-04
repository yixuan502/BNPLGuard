# Stage 4 candidate comparison and frozen selection

Completed 4 November 2026 in /Users/oneone/Desktop/BNPLGuard using its Python 3.13.13 .venv. Stage-three Dummy/LR were reused: prior reproducibility records and nine existing tests passed, original artifact hashes/config snapshots matched, and saved validation predictions were reproduced without refitting either baseline.

## Predeclared design

The unchanged ENDSMEET mapping, eight inputs and fixed 3810/1270/1270 split were reused. Data and split SHA256 are frozen in config/stage5_frozen.json. No data download, label change, exclusion of inconvenient observations or test evaluation occurred.

config/stage4_search.json was written before fitting. Four RF combinations: max_depth in [6,None] and min_samples_leaf in [5,20]; 200 trees, sqrt max_features, bootstrap=True, class_weight=None, random_state=42, n_jobs=1. Five shuffled stratified folds inside training only selected RF using mean AP. Among configurations within .005 AP of the best, prefer depth6 then larger leaves. This pragmatic regularization rule is not a statistical equivalence test. Full fold scores and IDs are saved; no fitted preprocessing is shared across folds.

Best five-fold mean AP=.755523 (unlimited depth, leaf20); the prespecified near-tie rule chose depth6/leaf20, mean AP=.751599. Only this RF specification proceeded to validation. This is a bounded search, not evidence that every possible RF configuration is inferior.

Sigmoid calibration was also predeclared for LR and the chosen RF. CalibratedClassifierCV wraps the complete raw-input Pipeline, uses five shuffled training folds and ensemble=False. Calibration scores come from training-only out-of-fold predictions; the inference base estimator is fitted on all original training rows. LR calibration uses decision_function; RF uses predict_proba. Neither validation nor test labels fit a calibrator. No isotonic search was added.

## Actual validation results

n=1270; positives491 (38.6614%). Every classification metric uses **threshold0.5**, fixed in advance. Dummy precision is undefined because it predicts no positives. AP is average precision, not trapezoidal PR-AUC.

| Model | AP | ROC-AUC | Brier | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| dummy | 0.386614 | 0.500000 | 0.237144 | N/A | 0.000000 | 0.000000 |
| logistic_regression | 0.720857 | 0.816946 | 0.167396 | 0.724537 | 0.637475 | 0.678223 |
| random_forest | 0.717325 | 0.812763 | 0.173677 | 0.726804 | 0.574338 | 0.641638 |
| logistic_sigmoid | 0.720857 | 0.816946 | 0.167281 | 0.724942 | 0.633401 | 0.676087 |
| forest_sigmoid | 0.717325 | 0.812763 | 0.169610 | 0.725352 | 0.629328 | 0.673937 |

Main results are unweighted sample metrics. Weighted validation sensitivity, log loss, probability means, reliability bins and confusion matrices are in comparison.json. Raw and sigmoid-calibrated versions have identical AP/AUC here, consistent with monotonic score transformations. Classification changes reflect different probabilities crossing0.5.

## Fit gap and development stability

| Model | Apparent train AP | Validation AP | AP gap | Apparent train Brier | 3-fold train-CV AP mean | Fold SD |
|---|---:|---:|---:|---:|---:|---:|
| dummy | 0.386352 | 0.386614 | -0.000262 | 0.237084 | 0.386352 | 0.000455 |
| logistic_regression | 0.766945 | 0.720857 | 0.046088 | 0.155133 | 0.759464 | 0.011592 |
| random_forest | 0.771834 | 0.717325 | 0.054509 | 0.164976 | 0.750610 | 0.010750 |
| logistic_sigmoid | 0.766945 | 0.720857 | 0.046088 | 0.155230 | 0.759464 | 0.011592 |
| forest_sigmoid | 0.771834 | 0.717325 | 0.054509 | 0.156817 | 0.750610 | 0.010750 |

Training metrics are optimistic resubstitution values, not generalization estimates. RF's AP gap is .0545 versus LR's .0461. In the four-setting search, unlimited-depth/leaf5 reached mean apparent train AP=.8450 but CV AP=.7533, indicating greater overfitting. The restricted chosen RF moderates this, but still does not improve the validation result. No claim of zero overfitting is warranted.

Stability uses three shuffled stratified folds of the original training data (seed1729), shared across candidates. Calibration is nested inside each outer training fold. RF hyperparameters were already selected using the full training set, so these are conditional fixed-parameter diagnostics, not unbiased nested estimates of the entire search. CV folds overlap in training data; fold SD is not a confidence interval or a significance test. No alternate held-out split was selected.

## Selection and probability reliability

Predeclared finalist rule: retain models within .01 of the best validation AP, then within .002 Brier of the best remaining model, then prefer the simpler object in the order raw LR, calibrated LR, raw RF, calibrated RF. Dummy is the required baseline, not a selection finalist. Tolerances are practical complexity tradeoffs, not proof of equivalence.

All four non-Dummy candidates pass the AP tolerance. Only raw LR and calibrated LR pass the Brier tolerance, so **raw Logistic Regression is selected**. LR sigmoid improves Brier by only 0.00011476; that improvement is insufficient to justify additional calibration complexity under the predefined rule. RF sigmoid improves its Brier by 0.004067, but remains worse than raw LR. LR also has the highest raw validation AP/AUC and a simpler, inspectable categorical linear model. RF has marginally smaller fold AP SD, which does not outweigh these results or establish a significant stability difference.

No severe probability defect is established from these limited diagnostics. Calibration helps RF's probability error without improving ranking. LR mean validation probability is .3968 versus observed .3866; this small overall gap does not establish calibration across the probability range. Brier mixes calibration and discrimination; detailed calibration curves, uncertainty and subgroup reliability remain stage-five work. Do not claim that raw LR is fully calibrated or suitable for credit decisions.

## Frozen stage-five contract

Selected object: `models/cfpb/stage4_v1/logistic_regression.joblib`. It is byte-identical to the previously accepted stage-three LR; no train+validation refit occurred. Artifact SHA256 `6f8a82a70e38ae9d5f6143ca4b491d21932d480ca1b38e3d93f079c6794c06d8`.

Structured authoritative freeze: **config/stage5_frozen.json**. LR C=1, lbfgs, max_iter1000, no class weighting, random_state42; original eight categorical features, special-code mapping, employment grouping, training-mode imputation and one-hot encoding. Calibration=none. Threshold=.5 reference, no business cost optimization or approval interpretation. Exact learned coefficients remain in the trusted serialized object; no retraining is required for evaluation.

Stage-five evaluation must verify artifact/schema/label/data/split hashes, then evaluate this frozen object on the original test IDs without reselection. Candidate test comparisons, if reported, are descriptive only and cannot change this choice. Add uncertainty, ROC/PR/calibration curves, original-column permutation importance, subgroup counts/reliability and model-card updates. Preserve sample-level scope and label survey-weight sensitivity separately. Do not refit the deployment artifact and transfer the old evaluation silently.

## Acceptance and reproduction

Existing plus added tests: **13 passed in34.13 seconds**. New checks verify inner/outer fold membership excludes validation/test IDs, predeclared selection behavior, complete-Pipeline training-only calibration, persisted validation probabilities/metrics, frozen selection and protected hashes. No original raw/config/baseline/split changed. Candidate serialized predictions match memory after reload.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m pytest -q
# Optional fresh reproduction; use a directory that does not already exist:
.venv/bin/python -m src.compare_models --output-dir outputs/reproduce/stage4_run_01
```

Completed and partial run directories are protected. A shutdown cannot continue local training; status.json and per-step artifacts identify saved progress. Rerun incomplete work under a new output directory. No Kaggle, Australian evidence, app or LLM work was undertaken.
