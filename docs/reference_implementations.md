# Implementation references and attribution

The project implementation was written independently. No teammate Notebook code, third-party results or unknown pretrained models were copied. The specification permits a bounded search of two or three GitHub examples; it does not make that search a baseline prerequisite. One official example and its documentation were sufficient for this simple baseline.

- Repository: https://github.com/scikit-learn/scikit-learn
- Inspected file: `examples/compose/plot_column_transformer_mixed_types.py`, main branch, accessed 4 November 2026. Source: https://raw.githubusercontent.com/scikit-learn/scikit-learn/main/examples/compose/plot_column_transformer_mixed_types.py . An exact commit was not obtained and is not invented.
- License: `COPYING` was inspected; BSD-3-Clause, https://github.com/scikit-learn/scikit-learn/blob/main/COPYING . Public API composition patterns informed the implementation; complete example blocks were not copied.
- Example task: Titanic survival classification using numerical age/fare and categorical sex/pclass and other inputs, train/test splitting, training-only Pipeline fitting and CV search. This is not financial/CFPB validation evidence.
- Useful patterns: Pipeline and ColumnTransformer isolate preprocessing; OneHotEncoder(handle_unknown=ignore) supports unseen categories.
- Project changes: eight verified survey inputs; custom raw-code validation; training-mode imputation; no chi-squared selector, Titanic data, labels or metrics; explicit train/validation/test partitions; no repeated test scoring or RandomizedSearchCV.
- Official documentation checked during stage 3: https://scikit-learn.org/stable/auto_examples/compose/plot_column_transformer_mixed_types.html and https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html . Installed/tested sklearn version: 1.9.1. All dependencies are pinned in requirements.txt.
- The Kaggle Notebook's provenance and license were not audited. It was registered as a reference, not copied as an implementation. Availability in the desktop copy is recorded separately.

The CFPB Python 2.7 import stub is not the project's runtime code and does not justify installing an obsolete interpreter. Codex assisted with the current implementation; disclose this assistance and have the team review the work. This migration did not conduct a new web-source or library-version review: it reused and verified the pinned local environment.

## Stage 4 additions (4 November 2026)

The existing BSD-3-Clause sklearn repository review was reused. No new third-party implementation or external model result was copied. Local installed API signatures and official RandomForestClassifier and CalibratedClassifierCV documentation were checked. References: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html and https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html . Sigmoid calibration wraps the complete Pipeline; ensemble=False uses training-fold out-of-fold scores to fit calibration and a full-training base estimator for inference. No test or validation label fits a calibrator.


## 5 November extension references

The preserved Kaggle Notebook was reviewed as source evidence only: metadata datasetVersion ID 15502327, full-data scaling and retained outcome-like predictors were recorded. Its unknown code license and saved scores were not reused. New project Pipelines are independent implementations. Actual SHAP uses the installed package and its official LinearExplainer/Independent-mask documentation (https://shap.readthedocs.io/en/latest/generated/shap.LinearExplainer.html). No coefficient-only substitute, LIME, ensemble or copied generator was added. Package versions and original-core preservation are recorded in the extension acceptance receipt.
