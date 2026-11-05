# Experiment and maintenance log

## 4 November 2026: fixed stage-three experiment

Data: local NFWBS_PUF_2016_data.csv, SHA256 `3680d33576549a99a8dfd7f99d5661a36a8fc1aac0d66f2bf2ec5524695304d8`. Positive labels are 2/3; negative labels are1; 44 missing targets are excluded. Eight features were fixed from the Codebook and financial rationale before fitting.

Split SHA256: `7b2bddd4605e5c09319d4e9bfd69c209a6c094a32730ca18b31462df7712a9a5`. Sizes3810/1270/1270; seed42. Main metric: validation AP. Reference threshold0.5. No tuning, threshold search, calibration, RF or test evaluation.

| Run/model | Validation AP | AUC | Brier | F1 | Fit and predict seconds | Decision |
|---|---:|---:|---:|---:|---:|---|
| stage3_v2 Dummy prior | .386614 | .500000 | .237144 | .000000 | .038311 | Retain required comparator |
| stage3_v2 LR C=1 | .720857 | .816946 | .167396 | .678223 | .055137 | Better validation evidence than Dummy; not final deployment selection |

Artifact timestamp: `2026-11-04T15:30:29.994254+11:00` (Australia/Sydney). LR converged in 13 iterations with no warnings. Each model fitted its own preprocessing. AP is average precision, not trapezoidal PR-AUC. Validation positives491/1270. Dummy has no positive predictions, so precision is N/A. LR TN/FP/FN/TP=660/119/178/313.

Survey-weight sensitivity uses finalwt on the same validation predictions: LR AP=.729460/AUC=.812796/Brier=.173396; Dummy AP=.421926/AUC=.500000/Brier=.245170. No main metric, feature or model was changed in response. Fitting remains an unweighted sample baseline.

## Engineering history

1. stage3_v1 ran successfully with raw-code cleaning outside Pipeline. It is preserved as superseded history and must not be used in the application.
2. stage3_v2 serialized raw-code checks, missing mappings, employment grouping and schema inside Pipeline. Its mathematical design and validation results were unchanged.
3. The first `--output-dir` reproduction attempt failed before fitting because Path was not imported. The import was added. Pre-fix artifacts remain under `outputs/verification/stage3_v2_before_cli_fix/`. Canonical v2 was rerun using the original locked IDs.
4. `python -m src.train_model --output-dir outputs/verification/reproduce_stage3` completed. All 1270 validation probabilities and both weighted/unweighted metric sets matched canonical v2 exactly. No test predictions were generated.
5. The original suite reported9 passed in1.91s. Checks cover labels, special values, invalid/missing inputs, split isolation, training-only modes, serialization, unseen valid categories, metric calculations and artifact integrity. AP was independently recomputed at score thresholds; AUC by positive/negative pair comparisons. pip check found no conflicts.
6. All six initially supplied materials retained their original SHA256. The baseline chart was opened and checked against the metric JSON.

## 4 November 2026: desktop migration and English conversion

The user copied the project to `/Users/oneone/Desktop/BNPLGuard`. Before editing,38 source/config/test/script/model/data/split/reference files were compared with the prior project: none missing and none changed. Optional initial inputs outside the portable project layout are separately inventoried; this38-file result is not a claim that every original download was copied.

The copied .venv launchers referenced the former workspace. It was retained as `.venv.pre_migration`; a fresh environment was created at the desktop location and the exact requirements were installed. Existing datasets and trained models were not downloaded or retrained.

All project-authored documentation and future-stage instructions were converted to English. The data-dictionary generator was translated too; statistical calculations and preprocessing were unchanged. Historical model manifests remain untouched: their original source hashes describe training-time code. `outputs/migration/2026-11-04/` records the maintenance delta and current checks separately.

See `docs/migration_check.md` for actual acceptance results. Completed run directories remain protected. Declare the limited RF search and model-selection policy before stage 4, keeping the test set locked.

## Stage 4 completed: candidate selection

Four RF configurations with train-only five-fold CV, plus train-only sigmoid calibration for LR/RF and three-fold conditional stability checks. Predeclared rules: config/stage4_search.json. Candidate run: models/cfpb/stage4_v1. Full rationale: docs/model_selection.md.

| Model | AP | ROC-AUC | Brier | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| dummy | 0.386614 | 0.500000 | 0.237144 | N/A | 0.000000 | 0.000000 |
| logistic_regression | 0.720857 | 0.816946 | 0.167396 | 0.724537 | 0.637475 | 0.678223 |
| random_forest | 0.717325 | 0.812763 | 0.173677 | 0.726804 | 0.574338 | 0.641638 |
| logistic_sigmoid | 0.720857 | 0.816946 | 0.167281 | 0.724942 | 0.633401 | 0.676087 |
| forest_sigmoid | 0.717325 | 0.812763 | 0.169610 | 0.725352 | 0.629328 | 0.673937 |

Threshold0.5 throughout. Selected raw LR; RF depth6/leaf20 (200 trees) did not improve validation AP or Brier. LR sigmoid Brier improvement=.00011476, insufficient under the predeclared .002 tolerance. Raw LR train/validation AP=.766945/.720857; RF=.771834/.717325. Fold SDs=.011592/.010750 are descriptive, not uncertainty intervals. Structured freeze: config/stage5_frozen.json. Test remains unevaluated; original data/configs/splits/baselines unchanged. All13 tests passed. No new source download or out-of-scope modeling.

## Stage 5 formal evaluation completed

Predeclared config/stage5_evaluation.json, protocol and source checkpoint precede locked-test scoring. Frozen raw LR, Dummy and raw RF evaluated at0.5 on the same1270 respondents (491positive). No fitting, recalibration, model selection or split change.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | AP | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression (frozen) | 0.766142 | 0.723502 | 0.639511 | 0.678919 | 0.843158 | 0.763422 | 0.157295 |
| Dummy (prespecified) | 0.613386 | N/A | 0.000000 | 0.000000 | 0.500000 | 0.386614 | 0.237144 |
| Random Forest (prespecified) | 0.762205 | 0.732187 | 0.606925 | 0.663697 | 0.836302 | 0.766896 | 0.166682 |

LR AP95%CI[.725172,.802343], AUC[.821062,.864214], Brier[.145968,.168581], using2000 paired respondent-bootstrap draws(seed20261104). RF's small test AP lead does not reopen selection; paired LR-minus-RF AP95%CI[-.015864,.009062]. LR-minus-RF Brier95%CI[-.014105,-.004594]. CI scope is fixed-model empirical sample uncertainty, not training/search or complex-survey inference.

Validation permutation importance30repeats(seed20261105): savings.208307±.014293SD, income.029354±.008613, household size.012428±.004377. Calibration10equal-width bins showed local overestimation; no recalibration. Prespecified groups reveal low-income FPR.5909 and62+ recall.4583; detailed small groups flagged. Weights are separate point sensitivity, not the main bootstrap target. Existing stage-four stability reused.

24 tests passed in4.51s. Statistical endpoint assertions use floating-point tolerance; a synthetic missing-value fixture uses float dtype for pandas3. The historical stage3/4 no-test-output assertion now applies only to those development directories. None of these test maintenance changes affects evaluation/model data. All protected hashes remain unchanged. Figures were inspected individually. Source/plan/config/model/output evidence is saved in outputs/evaluation/stage5_v1. Full interpretation: docs/stage5_evaluation.md. Stage5 accepted; stage6 pending.

## Stage 6 deterministic financial simulator completed

This is an engineering/formula verification, not a new ML experiment. Frozen model/data/config/evaluation/model-card hashes were snapshotted before edits and119 existing files remained unchanged. No model scoring, fitting, calibration, label/split/threshold change or dataset download was required.

| Scenario | Cash buffer (AUD) | Change from current (AUD) | RTI | Coverage (months) |
|---|---:|---:|---:|---:|
| Current | 900 | 0 | 24.44% | 0.278 |
| Added BNPL | 700 | -200 | 28.89% | 0.263 |
| Income shock | 0 | -900 | 30.56% | 0.278 |
| Added BNPL + income shock | -200 | -1100 | 36.11% | 0.263 |
| Reduced existing BNPL | 1100 | 200 | 20.00% | 0.294 |

Illustrative scenario—not empirical model results. Original supplied inputs4500/2500/700/400/200/1000, AUD; income drop.2 and hypothetical B0 reduction200. All five buffer results and the current ratios1100/4500 and1000/3600 match the specified expectations. Scenarios are immutable independent changes from current; only the labeled combined case applies both shocks.

87 new simulator cases plus24 prior cases:111 passed in3.40s. Checks include exact-decimal cancellation, extreme finite numbers, zeros/N/A, illegal types/ranges,100% income shock, reduction limits,200 seeded monotonicity cases and standalone standard-library operation. RTI-delta display was clarified to percentage points; the initial demo export was preserved and the canonical export regenerated with the same financial results. Chart opened and verified.

Current evidence: outputs/simulator/stage6_demo_v1 and stage6_acceptance.json. Method/API: docs/simulator_method.md. Stage6 accepted; stage7 not started. Kaggle modeling, Australian expansion, Streamlit and LLM remain outside this round.

## Kaggle specialist audit, 5 November 2026 (no model experiment)

Reread the local10345x17 CSV and verified its existing SHA256. Saved full profile, ID/date checks, sentinel/boundary/IQR diagnostics, descriptive label co-occurrence, candidate arithmetic identities,17-field dictionary and conditional historical-Notebook leakage review. No classifier, split, fitting or tuning was performed. Date gapJul2023-Jun 2024 and all-row algebraic dependencies are direct file findings; generation and label/window provenance are not authenticated.

Primary source/Notebook requests failed; exact-URL-linked third-party synthetic claim was recorded separately. DecisionC: no second model/current application module; proceed to core stage 7. Two English count/coverage charts were inspected. Four necessary audit checks passed, and 157 protected existing files were unchanged. Initial exploratory export and the earlier unit wording were retained as history; the final v1 table labels the DTI-named ratio's time/currency dimensions unknown. Evidence: outputs/kaggle_audit/v1 and docs/kaggle_data_audit.md.


## Independent second-source and explanation extension run (5 November 2026)

Supersedes the prior defer-only work restriction. Kaggle independent recorded-label classification is complete: 10 reviewed predictors, six excluded raw fields plus target, fixed 6207/2069/2069 split, training-fold Pipeline, eight candidates including Dummy, pre-test frozen RF at threshold 0.5/no calibration, then all three prespecified models evaluated once. RF test AP 0.566320, AUC 0.697078, Brier 0.206394; LR AP 0.568170, AUC 0.707620, Brier 0.207157. No test-driven reselection. RF has a large training/validation gap; paired LR/RF differences span zero. Presentation decision 2: report appendix only, no personal Kaggle endpoint. Original CSV and old audit artifacts remain unchanged. Page screenshot evidence now records CC0 1.0; synthesis, default criterion/window, currency/frequency/timing remain unresolved. Reference Notebook is preserved, directly reviewed and not executed/copied.

Actual SHAP 0.54.1 explains the frozen CFPB LR in log-odds with a fixed 200-row training-only background, seed 20261105. Four fictional/missing examples and original-eight-feature aggregation reconstruct decision_function/predict_proba to floating-point precision. A second prespecified reference illustrates background sensitivity. The base model card is unchanged; model_card_extensions.md adds the explanation scope while retaining local calibration/subgroup concerns.

Offline English result templates and stable model/simulator service interfaces run successfully. The optional adapter is disabled and limited to approved phrasing/order; no provider/client/key/API or real financial-data transmission occurred. Mock authorization, missing configuration, invalid edits, omitted limitations, exception and timeout fallbacks passed. **LLM adapter prepared, not live-tested.** Shared assumptions are stated once; no model prediction or financial arithmetic is delegated to text generation.

Australian evidence register includes issued ASIC guidance, historical research and the current Act compilation/original sections. Context only; no external-validation claim or simulator compliance thresholds. No Streamlit or deployment work occurred.

Acceptance: 23 extension checks passed; full suite **138 passed in 3.55s**; CFPB data audit PASS. All 221 prior protected files, core dependency versions, fixture probabilities and complete simulator output remain unchanged. Three new charts were visually inspected. Evidence: outputs/extensions/acceptance_v1.json, outputs/kaggle_experiment/v1, outputs/explanations/cfpb_shap_v1 and outputs/extensions/demo_v2. Reproduction and API contracts: docs/extensions_handoff.md. Next: stage 7 integration of frozen CFPB+SHAP, simulator and offline template; Kaggle remains appendix-only and LLM remains disabled.


## Stage 7 completed: local application (5 November 2026)

One English Streamlit app now integrates Screen/Stress/Explain/Model, frozen CFPB prediction + actual SHAP, unchanged independent simulator and existing offline templates. Schema options retain USD annual-household/person/monthly scopes; no initial automatic score. Submitted snapshots bind results; edits invalidate old output. State is session-local; caches contain trusted resources/static evidence only. Model/SHAP/evidence failure states are explicit. Kaggle remains appendix-only; LLM disabled, no external API or financial-input logging.

13 application cases passed (5.21s); full suite **151 passed in 5.63s**; CFPB audit PASS; pip check clean. All 369 pre-existing captured files and core dependency versions remain unchanged. Prior simulator response exactly retained, including 900/700/0/-200/1100 buffers. No refit/calibration/threshold/metric/background change.

Actually started at http://127.0.0.1:8501 and inspected in desktop Chrome and 390x844 phone emulation. Four areas, empty/fictional states, SHAP/currency, signed scenarios, saved evidence, input invalidation and responsive stacking were checked. Actual screenshots/QA/receipt: outputs/app/stage7_v1. Missing-file and zero/invalid-input paths were AppTest/mock checks, not manual browser fault injections. Physical devices/additional browsers, remote publication and real-user research are not claimed.

Entry app.py; layers src/app_inputs.py, app_state.py, app_services.py, app_charts.py, app_ui.py; tests/test_app.py; requirements-app.txt/requirements-app-lock.txt. Docs/stage7_app.md records architecture, commands, privacy and stage-eight conditions. Local server remains running with a clean Screen session; PID/port are in the receipt. Next: explicit stage-eight repository/hosting scope, artifact allowlist, environment compatibility and deployed-URL acceptance.


## Stage 8 engineering record: deployment only (5 November 2026)

The stopped local service was restored from the desktop project .venv at http://127.0.0.1:8501. Actual browser recovery required reloading the disconnected session. A fictional questionnaire produced 83.85% with matching SHAP/template; the Stress fictional example ran. This is local evidence, not public online acceptance.

The verified GitHub account is yixuan502; a previously absent private yixuan502/BNPLGuard repository has been created. The desktop directory had no existing Git history; it is now initialized without replacing any history. Course code-access requirements permit a private repository with instructor access. Repository and public-app visibility are separate.

A default-deny release allowlist excludes raw CSVs, per-row predictions/bootstrap draws, course PDFs, reference Notebooks, backups, environments, secrets and real-user inputs. Dedicated fictional/source configs remove runtime dependence on local research receipts. uv.lock and Python 3.13 pin the unchanged core/runtime package versions; every locked registry package has a compatible CPython 3.13 Linux x86_64 wheel in lock metadata. Actual Cloud build verification is still pending. Three meaningful packaging tests were added; the local full suite passed 154 tests in 6.41s. The initial whole-tree pytest attempt collected temporary release copies; testpaths now limits discovery to the canonical tests directory. Initial 45-second cold-start smoke timed out while initializing fresh dependencies/font cache; a longer isolated check is in progress. No numerical algorithm was changed to pass a test.

All 192 pre-stage-eight protected model/data/config/evaluation/core files match their original SHA256 values. Source/model selection, background, label, split, threshold, formal metrics and simulator arithmetic remain fixed. LLM is disabled and Kaggle remains appendix-only. Logs and preservation evidence are local under outputs/deploy/stage8_v1. No public URL or anonymous acceptance is claimed yet. Community Cloud is at a sign-in/terms page; user account actions will be requested after the repository and portable checks are ready. Real-user feedback remains stage nine.


### Isolated release check passed

The new raw-data-free checkout with its own uv-created .venv passed all four areas in 72.488 seconds including first-run dependency/font-cache initialization. Probability 0.8384946129177755, maximum SHAP reconstruction error 6.661338147750939e-16; simulator buffers 900/700/0/-200/1100; saved Model metrics AP 0.7634/AUC 0.8432/Brier 0.1573. No unavailable-evidence warning occurred. The 45-second initial deadline was too short for that cold start; the portable check now allows 120 seconds. This is an isolated AppTest run, not anonymous public acceptance.


## Private GitHub release verified; Cloud login pending

Repository: https://github.com/yixuan502/BNPLGuard (private), branch main, entry app.py, Python 3.13, no secrets. Initial app release commit: ffa92490dcf1c38793afe7d6313ae02beddc63e5. The actual remote repository was cloned afresh, with all 98 reviewed files, no raw data and its own uv-locked .venv. All four AppTest areas passed in 81.745 seconds, including first-run font-cache initialization. Prediction, SHAP, offline-template, five simulator buffers and aggregate Model metrics matched the isolated-tree check. This verifies the published file set and is not cloud/anonymous acceptance. Later documentation/ignore-policy commits do not alter the validated numerical app behavior.

The required local data audit also passed: 6394x217, 6350 eligible, 2454 positives. Original protected files remain unchanged. The local service was restarted again after portable-path changes; its actual terminal URL is http://127.0.0.1:8501. The fictional questionnaire and eight-input SHAP/template were rechecked in the browser after restart. Release exceptions are root-anchored; unrelated nested documentation remains ignored.

The only current external blocker is Community Cloud sign-in/terms and any GitHub OAuth authorization. The user must complete those account actions in the browser, without sending passwords/tokens in chat. Then select repository yixuan502/BNPLGuard, branch main, app.py, Advanced Python 3.13, and no secrets. If private repository authorization is required, grant only the repository access needed. Deploy, inspect real build logs, set application Sharing to public (repository remains private), and verify a fresh browser with no Streamlit login. No actual cloud build, public URL or anonymous four-area check has occurred yet. Do not send a guessed URL to the instructor. Real-user feedback remains a subsequent stage.


## Stage 8 completed: private GitHub source and public application (5 November 2026)

Public URL: **https://bnplguard-yixuan502.streamlit.app/**. Repository https://github.com/yixuan502/BNPLGuard remains private; main/app.py/Python3.13/no secrets. Initial deployed app revision c23178cd823ae6d70b4f2cfdb11576bad6793670. User completed account/terms/login; deployment and explicit public-app Sharing are complete. Cloud logs confirm successful uv-sync installation from uv.lock, unchanged core package versions and server startup. The 127.0.0.1 binding works through the platform proxy, verified by actual anonymous interaction; no network-protection change was made.

Actual separate anonymous-browser acceptance: Screen fictional submission83.85%, matching eight-input SHAP/template and log-odds reconstruction errors below7e-16; Stress buffers900/700/0/-200/1100AUD; Explain Global/Local/Scenario; Model saved metrics, ROC/PR/reliability, subgroup/weight limits and context/appendix notes. A fresh second viewer session had blank inputs and no previous prediction or owner controls. No login prompt was required. Physical devices, additional browsers/networks and real-user comprehension were not tested remotely.

Local full regression154passed; local auditPASS; isolated release and actual GitHub-clone AppTestsPASS;192protected files unchanged. No refit, formal-metric recomputation, calibration, split/feature/threshold/background or simulator arithmetic change. LLM disabled, not live-tested; Kaggle appendix only. Actual public capture in docs/images/app_public.jpg; detailed receipts/logs/screenshots locally in outputs/deploy/stage8_v1; current method in docs/deployment.md. Final publication records are a later documentation-only main commit. Private source access for the instructor remains a handoff item if required. No technical blocker remains for stage-nine consented user feedback; it has not yet started.


## 5 November 2026: feedback receipt, not a new model experiment

Read-only OOXML review of a user-supplied three-participant compilation. Existing simulator independently reproduced both case keys; all36 item scores and summary arithmetic agree. Text16/18; final recorded app18/18 combines6 independent and12 post-operational-guidance items. S1 scores are retained as source-reported, not independently verified. Source workbook unchanged and private; aggregate JSON/note only are publication candidates. No training, test-set re-evaluation, calibration, threshold change, UI fix or report writing occurred.
