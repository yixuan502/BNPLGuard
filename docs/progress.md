# BNPLGuard progress

Updated 5 November 2026, Australia/Sydney. **Stages 1–6 complete. Stage 7 Streamlit integration is next.**

## Active project and preserved foundation

Root: /Users/oneone/Desktop/BNPLGuard. Interpreter: /Users/oneone/Desktop/BNPLGuard/.venv/bin/python. Python3.13.13 with pinned requirements. All project-authored material is English; user explanations may be Chinese. sources/, raw datasets and third-party reference files remain unchanged.

Stages1–3 established the official-document/course-PDF audit, selected-field dictionary and leakage review, fixed train3810/validation1270/test1270 IDs and accepted Dummy/LR. Stage4 added a bounded RF search and training-only calibration comparison and selected the original uncalibrated LR at0.5. Stage 5 preserved that exact fitted object, all eight inputs, label and splits. No model, raw data, protected config or previous result was overwritten.

## Stage 5 completed

- Predeclared protocol, bootstrap and subgroup plan; sealed evaluation source/config hashes before test scoring.
- Rechecked ID isolation, model/schema/hash identity and training-only imputer modes/encoder categories. No fit, selection or threshold/calibration change.
- Formally evaluated LR plus prespecified Dummy/raw-RF comparators on the same1270 locked test respondents:491positive,779negative.
- Saved individual predictions, metrics/undefined reasons, ROC/PR coordinates, confusion matrices and five English figures.
- Saved2000 paired iid respondent-bootstrap draws/indices and percentile95% intervals, seed20261104; weighted point sensitivity separately.
- LR reliability:10equal-width bins with counts/Wilson intervals and probability distribution. No corrective calibration fitted.
- Validation-only whole-Pipeline permutation importance, AP scoring,30repeats, seed20261105. Reused stage-four development stability without fitting.
- Prespecified age/income audits include n, positive/negative counts, recall/FPR/other defined metrics, Wilson intervals and small-group flags.
- **24 tests passed in 4.51s.** All protected artifacts/config/data/split hashes remain unchanged. All five figures were opened and inspected.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | AP | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression (frozen) | 0.766142 | 0.723502 | 0.639511 | 0.678919 | 0.843158 | 0.763422 | 0.157295 |
| Dummy (prespecified) | 0.613386 | N/A | 0.000000 | 0.000000 | 0.500000 | 0.386614 | 0.237144 |
| Random Forest (prespecified) | 0.762205 | 0.732187 | 0.606925 | 0.663697 | 0.836302 | 0.766896 | 0.166682 |

All classification metrics use0.5. LR95%CI: AP[.7252,.8023], AUC[.8211,.8642], Brier[.1460,.1686]. No descriptive performance decline from validation. RF AP is slightly higher on test, but paired difference includes zero; the frozen LR remains selected. Full evidence and honest limits: docs/stage5_evaluation.md and docs/model_card.md.

## Material findings and limitations

- Supports identifying contemporaneous self-reported difficulty in this survey distribution above a prior-only comparator. Does not establish BNPL default, future prediction, causality, Australian validity or safe credit decisions.
- Mean LR forecast40.11% versus observed38.66%; local overestimation in some bins. Neither raw/no-calibration status nor Brier proves overall calibration.
- Savings is the dominant global permutation feature, then income and household size. Importance is not a personal or causal explanation.
- LR subgroup errors vary:62+ recall45.83%; income-underUSD30000 FPR59.09%. No fairness claim. Small detailed18–24 and70–74 groups have limited precision. No group-specific thresholds were optimized.
- Bootstrap reflects fixed-model/empirical-test-sample uncertainty only, not model fitting/selection or complex survey design. Primary metrics are unweighted; finalwt sensitivity is separately labeled.
- Savings special missingness18.52%, employment/resource proxies and self-report/context mismatch remain. Unused PCTLT200FPL47-record frequency discrepancy and official-server byte-identity limits remain documented.
- Kaggle CSV10345x17 has now received the5 November specialist audit: decisionC, deferred for modeling and excluded from the current application; primary provenance/license/label timing remain unresolved. No Australian extension, Streamlit or LLM work occurred.
- Moodle dates/sign-off, student contributions, AI review/disclosure and later real user research/report/video remain outstanding.

## Files and reproduction

Frozen deployment contract: config/stage5_frozen.json (unchanged). Evaluation plan: config/stage5_evaluation.json. Results: outputs/evaluation/stage5_v1. Source: src/evaluate_frozen.py and src/evaluation_stats.py. Figures: scripts/plot_stage5.py. Completion receipt records evaluation and visual evidence; historical stage3/4 manifests remain training-time records.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m src.evaluate_frozen --verify-only
.venv/bin/python -m pytest -q
.venv/bin/python scripts/plot_stage5.py
```

For deliberate reproducibility only, run evaluation with a new --output-dir; no refitting or selection is allowed. Completed directories are protected. Regenerating figures reads saved results only. Local computation stops on shutdown.

## Stage 6 completed

Implemented independent numeric validation, pure monthly formulas, immutable scenario inputs and serializable English presentation. New source: src/input_validation.py, src/bnpl_simulator.py, src/simulator_presentation.py, src/simulator_demo.py. The financial calculator needs only the Python standard library and reads no model or dataset.

Inputs I/E/D/B0/Bnew/S, default currency AUD; strict finite/nonnegative numeric values, explicit fraction0..1 income shocks and reduction0..B0. Five scenarios derive independently from current, with the combined scenario explicitly applying both changes. Each returns effective inputs, metrics, scenario-minus-current deltas, assumptions and rule messages. RTI changes display percentage points.

| Scenario | Cash buffer (AUD) | Change from current (AUD) | RTI | Coverage (months) |
|---|---:|---:|---:|---:|
| Current | 900 | 0 | 24.44% | 0.278 |
| Added BNPL | 700 | -200 | 28.89% | 0.263 |
| Income shock | 0 | -900 | 30.56% | 0.278 |
| Added BNPL + income shock | -200 | -1100 | 36.11% | 0.263 |
| Reduced existing BNPL | 1100 | 200 | 20.00% | 0.294 |

Illustrative scenario—not empirical model results. Source configuration: config/simulator_demo.json. Current table/JSON/chart/manifest: outputs/simulator/stage6_demo_v1. English method/API guide: docs/simulator_method.md. Initial export was retained separately when delta display units were clarified.

Final validation: **87 new simulator cases;111 tests passed in3.40s**, including the prior24 model/statistical tests. Exact arithmetic, division-by-zero N/A reasons, invalid fields/types/nonfinite values,100% income shock, invalid reduction, repeatability, no mutation and200 seeded monotonicity cases were checked. Standalone use without site packages passed.

The119 pre-existing protected model/data/config/evaluation/model-card files match their original hashes. No frozen estimator, feature, label, threshold, split or previous test result changed. The existing model card still records probability local overestimation and subgroup disparities. Preservation and test evidence: outputs/simulator/stage6_acceptance.json.

## Stage 7 next and limitations

**Ready for stage7 Streamlit integration; no technical blocker.** Build the Screen/Stress/Explain/Model views using the frozen ML artifacts and the independent simulator interface. Surface input definitions, same-currency/no-conversion assumptions,0..100% versus API0..1 mapping, invalid/partial states, N/A reasons, original versus combined scenarios and the existing model limitations. Do not sum cash-flow metrics and ML scores into an unvalidated probability or link monetary sliders to survey model inputs implicitly.

The monthly simulator has no dated calendar, fee/interest or multi-month depletion engine. Coverage assumes no new income and unchanged outflows; positive monthly buffer does not ensure every due date is funded. Reducing B0 is hypothetical, not contract modification. Future real-user research is required for RQ2. No complete UI, deployment, Kaggle modeling, Australian expansion or LLM is implemented. Kaggle specialist audit is complete; decisionC defers modeling and excludes it from the current application.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m pytest -q tests/test_simulator.py
.venv/bin/python -m pytest -q
.venv/bin/python -m src.simulator_demo --output-dir outputs/simulator/pycharm_demo_01
```

Use a new output directory for another demo. PyCharm interpreter remains /Users/oneone/Desktop/BNPLGuard/.venv/bin/python. Direct run_simulation API calls are deterministic and write no user inputs. Stage-five verification reads existing evidence only; no formal evaluation rerun is needed for simulation.

## Kaggle specialist audit completed (5 November 2026)

This explicitly authorized branch was completed after stage 6 and before stage 7. It did not reopen core model/simulator work. Local CSV reread:10345rows,17fields, SHA256 780cdb1eec43519b0764059563d89258ef1d9e4cef3b1ffdeab9622d6976b1bd, no ordinary missing/duplicate rows/duplicate IDs; flag 1=4040(39.0527%). Semantic grain remains unknown despite one row per ID. Dates coverJan-Jun 2023 andJul-Dec 2024 with a 12-month gap.

Primary Kaggle card/current Notebook and public APIs were unavailable; version/license/origin/generator and key units/timings remain unknown. A third-party exact-URL-linked synthetic claim is recorded as auxiliary, not authenticated publisher evidence. All local rows numerically match purchase/income for the DTI-named field and a credit/delay/miss expression for risk_score. These are arithmetic dependencies, not verified generation code or a label rule. No application-time history or valid future default target was established.

Decision **C: defer second-source modeling and exclude it from the current application**. Audit-only EDA may support a methodology appendix, with provenance warnings. No Kaggle financial case was fabricated and no second model is warranted now. Continue directly to stage 7 Streamlit using the core CFPB model and independent simulator.

Deliverables: src/kaggle_audit.py; docs/kaggle_data_audit.md; kaggle_sources.md; kaggle_data_dictionary.md; kaggle_leakage_review.md; updated data_source_decision.md; source access logs and field evidence in data/metadata; quality tables and two visually inspected English figures in outputs/kaggle_audit/v1. Four audit checks passed; the full project regression suite passed **115 tests in 4.57s**. The existing CFPB audit gate passed with byte-identical audit outputs. The 157 pre-existing model/data/config/source/test/evaluation/simulator/model-card files remain hash-identical. No training, merge, Streamlit, LLM or Australian work occurred.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m src.kaggle_audit --verify-only
.venv/bin/python -m pytest -q tests/test_kaggle_audit.py
.venv/bin/python -m src.kaggle_audit --output-dir outputs/kaggle_audit/reproduce_01
```

Use a new directory for recalculation. Optional public-source refresh is separate and cannot automatically change the curated decision. Current account access gaps do not block stage 7; there is no independent Kaggle experiment to finish first.


## Second-source and explanation extensions started (5 November 2026)

Current scope is the explicitly authorized extension round, superseding the prior defer-only work restriction. Registered page screenshots and the preserved Notebook. Captured core artifact and prediction/simulator baselines. Kaggle experiment protocol is sealed before training; no model evaluation is yet claimed for this new experiment. Completion evidence will be appended after actual checks.


## Authorized extensions completed (5 November 2026)

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


## Stage 8: release preparation and local recovery (5 November 2026)

The stopped local service was restored from the desktop project .venv at http://127.0.0.1:8501. Actual browser recovery required reloading the disconnected session. A fictional questionnaire produced 83.85% with matching SHAP/template; the Stress fictional example ran. This is local evidence, not public online acceptance.

The verified GitHub account is yixuan502; a previously absent private yixuan502/BNPLGuard repository has been created. The desktop directory had no existing Git history; it is now initialized without replacing any history. Course code-access requirements permit a private repository with instructor access. Repository and public-app visibility are separate.

A default-deny release allowlist excludes raw CSVs, per-row predictions/bootstrap draws, course PDFs, reference Notebooks, backups, environments, secrets and real-user inputs. Dedicated fictional/source configs remove runtime dependence on local research receipts. uv.lock and Python 3.13 pin the unchanged core/runtime package versions; every locked registry package has a compatible CPython 3.13 Linux x86_64 wheel in lock metadata. Actual Cloud build verification is still pending. Three meaningful packaging tests were added; the local full suite passed 154 tests in 6.41s. The initial whole-tree pytest attempt collected temporary release copies; testpaths now limits discovery to the canonical tests directory. Initial 45-second cold-start smoke timed out while initializing fresh dependencies/font cache; a longer isolated check is in progress. No numerical algorithm was changed to pass a test.

All 192 pre-stage-eight protected model/data/config/evaluation/core files match their original SHA256 values. Source/model selection, background, label, split, threshold, formal metrics and simulator arithmetic remain fixed. LLM is disabled and Kaggle remains appendix-only. Logs and preservation evidence are local under outputs/deploy/stage8_v1. No public URL or anonymous acceptance is claimed yet. Community Cloud is at a sign-in/terms page; user account actions will be requested after the repository and portable checks are ready. Real-user feedback remains stage nine.


### Isolated release check passed

The new raw-data-free checkout with its own uv-created .venv passed all four areas in 72.488 seconds including first-run dependency/font-cache initialization. Probability 0.8384946129177755, maximum SHAP reconstruction error 6.661338147750939e-16; simulator buffers 900/700/0/-200/1100; saved Model metrics AP 0.7634/AUC 0.8432/Brier 0.1573. No unavailable-evidence warning occurred. The 45-second initial deadline was too short for that cold start; the portable check now allows 120 seconds. This is an isolated AppTest run, not anonymous public acceptance.
