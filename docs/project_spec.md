# FINS5557 Track A: BNPLGuard execution specification

Updated 4 November 2026. Maintained English edition of the user's v2 specification, incorporating the explicit desktop-location and English-language instructions. The original wording is preserved in the migration archive. This is a specification, not evidence that planned stages are complete. Read progress.md for actual status.

## 1. Background and collaboration

The project is a three-person UNSW FINS5557 Applied AI in Finance Track A assignment. The user works on Apple Silicon in PyCharm, with experience in pandas, sklearn, portfolio backtesting and Streamlit. Explain financial logic, methodological choices and reproduction steps without repeatedly teaching elementary Python.

Write every project-authored file in English, including existing and future documentation, comments, generated outputs, application copy and report/video materials. Use clear student-level language without inflated claims. This supersedes the original request for Chinese project explanations. Conversation language may follow the user's immediate preference.

Deliver runnable files, execute checks, and distinguish actual results from expected results. For each stage record completion, reasons, changed files, commands, actual output, remaining problems and next steps. Use labels such as PyCharm setup, Terminal command, Expected output and Actual result. Make ordinary technical decisions from evidence without repeated approval requests. Ask only for essential information that cannot be inferred, account actions or material scope changes. Verify accessible files and actual paths; preserve existing user work and read AGENTS.md first.

## 2. Fixed project direction

**BNPLGuard — AI-Powered Financial Vulnerability Screening and BNPL Repayment Stress Simulation.**

CFPB National Financial Well-Being Survey is the primary real survey dataset. Kaggle BNPL is a candidate auxiliary source to audit after the first CFPB baseline works, not a mandatory second model.

- RQ1: Can traditional ML identify consumers who report difficulty covering expenses and paying all their bills in a typical month? Wording must match the verified questionnaire. Use Dummy comparison, locked test evaluation, probability reliability and uncertainty.
- RQ2: Can an interactive BNPL repayment stress simulator help users understand the financial pressure of additional instalment payments? Answer with real comprehension tasks, scenarios and feedback, not ML AUC.
- Optional RQ3: What transaction-level demonstration or independent experiment can audited Kaggle data add? Synthetic data support only conclusions about their simulated setting.

The architecture is ML Screening + Financial Scenario Analysis + Explainable Dashboard. Intended users are BNPL analysts and financial-institution product/risk teams. Keep Financial Vulnerability; do not convert the project into an ordinary BNPL Default Predictor. Traditional validated ML satisfies AI-Powered; an LLM is not required. Do not add RAG, forecasting, complex recommendation engines or deep learning by default. Innovation lies in interpretable screening combined with scenario comparison and usability. Do not assume RF will win.

## 3. Interpretation boundaries

CFPB is not a BNPL loan ledger. A same-period survey label supports cross-sectional classification/screening, not future default prediction or a validated early-warning system.

| Output | Supported interpretation | Unsupported interpretation |
|---|---|---|
| Model probability | Estimated probability under the specified self-report label | Real BNPL default probability or an inevitable personal outcome |
| Cash buffer and related formulas | Cash-flow arithmetic under explicit assumptions | ML prediction or compliant credit approval |
| Feature importance | Contribution to this model's predictive behavior | Causal effect |
| User testing | Preliminary prototype usability evidence | Market effectiveness or credit-prediction validity |

Do not sum model scores and financial indicators into an unvalidated probability. Simulator sliders change formula results; they do not change validated model risk without legitimate input mapping and evaluation.

## 4. Materials and source status

Initial materials: project-a-tech-team.pdf, marking-criteria-a-tech-team.pdf, a bnpl-credit-risk-insights Notebook (possibly numbered copies), and NFWBS_PUF_2016_data.csv. The current inventory identifies their actual available locations.

CFPB entry: https://www.consumerfinance.gov/data-research/financial-well-being-survey-data/ . Historical CSV link: https://files.consumerfinance.gov/f/documents/NFWBS_PUF_2016_data.csv . Verify data, Codebook, instrument and methods against official material. The initial6394-row/217-variable figure was a hypothesis until locally checked.

Kaggle candidate: https://www.kaggle.com/datasets/shree0910/buy-now-and-pay-later-fintech-ml-dataset . A Notebook is not the raw CSV. Previous claims of10345 rows,17 columns or synthetic generation require evidence. Preserve downloaded files and do not redownload available data. Retrieve only missing official explanatory material when needed. Current results are in progress.md; earlier plans or sample code are not completed training or deployment.

## 5. Course requirements

Read available course PDFs and record file/page evidence in rubric_checklist.md. If unavailable, mark requirements unconfirmed and continue independent work. Do not invent quotations, points, pages or dates. Previously discussed page/video limits, testing counts, score weights, pitch and final weeks must be checked against the actual PDFs. Follow course AI-use, attribution and individual-contribution requirements. Current PDFs are available and their checked requirements are in the checklist; actual semester dates and sign-off still require Moodle evidence.

## 6. Stage 1: location, environment and structure

### 6.1 Root and PyCharm

The user explicitly selected `/Users/oneone/Desktop/BNPLGuard` as the active root after copying the first baseline there. All subsequent project edits belong there; do not create a nested BNPLGuard folder or modify other course projects or the former workspace. Verify actual command working directories. If remote access cannot reach the desktop, state that rather than claiming files were saved there.

Create/reuse a dedicated .venv, check interpreter/package compatibility and do not modify system Python. Rebuild a copied environment if it retains obsolete launchers. Document PyCharm's interpreter and working directory. The user authorizes ordinary project file changes, dependency installation, legal public-source access, training and checks within the current scope. Preserve originals and user modifications.

Keep this specification in docs/project_spec.md, concise project instructions in AGENTS.md, and progress in docs/progress.md. Preserve compatible instructions; document conflicts. sources/ remains read-only reference material. Do not rewrite raw datasets or third-party references simply to change project language.

### 6.2 Engineering

Preferred stack: Python, pandas, numpy, sklearn, joblib, Streamlit, matplotlib/plotly, pytest. Choose tested deployment-compatible versions. No database, paid API or complex cloud architecture is required. Train offline and load trusted persisted artifacts; never retrain each time the app opens.

Use pathlib-rooted paths, module commands such as python -m src.data_audit, fixed seeds, hashes, configurations, row-flow counts and environment records. Maintain meaningful directories as needed: config/, data/raw/cfpb/, data/raw/kaggle_bnpl/, data/processed/, data/splits/, data/metadata/, src/, models/, outputs/tables|figures|metrics/, tests/, docs/. Create source modules and documents when their stage requires them, not empty placeholders falsely presented as completion. Suggested later modules include evaluate_model, explain_model, input_validation, bnpl_simulator and the Streamlit app.

## 7. Stage 2: CFPB feasibility gate

### 7.1 Sources and quality

Keep raw files unchanged. Record URLs, actual acquisition dates where known, release/year, checksums and verified usage conditions. Check dimensions, types, IDs, duplicate rows/IDs, ordinary missingness, special codes and illegal categories. Establish grain, sampling, weights and cross-split grouping risks. Do not treat every negative number as missing; interpret refusal, unknown, skip and legitimate values field by field. Weights are not predictors. State whether estimates concern the unweighted sample or population weighting. Explain any weighted sensitivity and its limitations; ordinary bootstrap is not complete complex-survey inference.

### 7.2 Label

Verify ENDSMEET against official wording and values, not its name or chat history. Record the original question, each category, missing treatment, binary mapping, class counts, prevalence and exclusions. Never impute a missing target as no difficulty. Fix the main definition before performance; reasonable alternatives are separate sensitivity designs, not labels selected for the best score. If unsuitable, explain and select a defensible real difficulty outcome without fabricating default labels.

### 7.3 Features and leakage

Choose a compact, interpretable resource/employment/savings/debt feature set; roughly6–12 inputs is a workload guide, not a rule. For each field document original wording or source, coding, missing rules, rationale, sensitivity, proposed app prompt, availability and relation to the label. Exclude the label and deterministic transforms, IDs, meaningless fields, overlapping hardship questions and potentially overlapping composite scales. Inspect FWB scores carefully. Distinguish direct leakage from legitimate concurrent association. Without timing evidence, restrict claims to concurrent screening. Prefer age and other sensitive attributes for subgroup audit rather than predictors; justify any inclusion.

Gate evidence: traceable source, genuine defensible label, complete selected-field codes, no obvious leakage and adequate classes. If the gate fails, revise honestly; do not invent data.

## 8. Stages 3–4: baselines and candidate selection

Stage 3 runs DummyClassifier(strategy=prior) and LogisticRegression and saves real validation results. Stage 4 adds RandomForestClassifier, limited tuning and selection. Do not start with XGBoost, neural networks or large searches. Ordinary cleaning, feature and parameter decisions may be made from evidence; material scope changes must be identified.

### 8.0 References

A bounded search of2–3 GitHub implementations is optional; also check official APIs. Read source, license, target, preprocessing timing, splits, labels and dependencies before reuse. Record repository/file/commit if known, license, useful patterns, flaws and adaptations in reference_implementations.md. Do not copy unlicensed code, metrics, figures, reports or unknown pickled models. Refit on this project's training data. If access is unavailable, record the gap and independently implement using verified interfaces; GitHub login must not block baselines.

### 8.1 Splits and preprocessing

Start from stratified60/20/20, random_state42 if grain permits. Use group isolation when people repeat; temporal splitting requires genuine temporal meaning. Save split IDs and lock test data against feature/model/threshold/calibration/tuning decisions. Every candidate owns separate Pipeline and ColumnTransformer instances. Fit imputation, scaling, selection and resampling on training data/folds only. Prefer one-hot categorical encoding with unknown handling as model protection; the app must still reject illegal inputs. Scale real numeric LR inputs when needed; RF does not require scaling for symmetry. Income codes are not dollars; ordinal treatment requires a dictionary rationale.

### 8.2 Training and comparison

Record config, time, counts and validation evidence. Starting values may include LR max_iter1000 and RF200 trees/min_samples_leaf5; assess convergence and overfitting. Compare mainly by validation average precision, also AUC, Brier and classification metrics. AP depends on prevalence and is not trapezoidal PR-AUC. Predeclare small searches. Class weighting, depth/leaf limits or resampling require evidence; no automatic oversampling. Near ties should consider stability, calibration, interpretation and complexity rather than a0.001 advantage.

## 9. Stage 5: evaluation, explanation and reliability

After freezing the design, evaluate candidates on the same locked test set; do not use test results to reselect. Report n, prevalence, Accuracy, Precision, Recall, F1, AUC, AP, Brier, confusion matrix, ROC/PR curves and calibration plot. State threshold origin:0.5 reference or development-only business choice with false-positive/negative tradeoffs. Do not invent industry risk cutoffs. Handle undefined metrics with N/A and reasons. Add uncertainty when supported, explaining assumptions.

Choose calibration before testing. Training-only CV calibration may be compared on validation, but do not reuse a small validation set endlessly for every decision. Never fit a calibrator on test labels. Probabilities remain estimated; calibration does not prove Australian transportability. The deployed artifact must match the evaluated object. If refitted on additional data, record the new object and do not silently transfer an old test score.

Use repeated permutation importance on original input columns through the full Pipeline, preferably on validation, with metric and variation stated. Global importance is not a personal causal explanation. SHAP is optional. Correlated features can share importance. Check a few seeds/CV within development data without selecting favorable test sets. Report subgroup counts, metrics and uncertainty; small samples and similar metrics do not prove fairness. Maintain a model card.

## 10. Stage 6: independent BNPL stress simulator

This deterministic module is independent of Kaggle and ML. Inputs: monthly after-tax income I, essential living costs E, existing non-BNPL debt payments D, existing BNPL payments B0, added BNPL payments Bnew, accessible emergency savings S. Let B=B0+Bnew. Avoid double-counting repayments in E, D and B.

```
Repayment-to-Income Ratio = (D + B) / I
Monthly Cash Flow Buffer = I - E - D - B
Emergency Savings Coverage = S / (E + D + B)
```

Coverage assumes unchanged costs/payments and no new income; it is not actual depletion time with continuing income. Reject nonfinite, negative and nonnumeric inputs. When I=0, calculate buffer but show RTI as N/A; never force income to1. Handle zero coverage denominator explicitly.

Scenarios: current, added BNPL, reduced income, reduced BNPL. Label monthly-payment simplification. If purchase/instalment/frequency inputs are added, state deposit, interval, fees and start date. Fortnightly is not exactly twice monthly; use dated payments or explicitly approximate monthly averages. Positive monthly buffer does not guarantee sufficient funds on every due date.

Illustrative arithmetic, not empirical findings: I4500/E2500/D700/B0400/Bnew0/S1000 gives buffer900, RTI24.44%, coverage0.278 months. Adding200 BNPL gives buffer700. A separate20% income reduction from the original case gives buffer0. A separate200 reduction in original BNPL gives buffer1100. State whether shocks are independent or cumulative. Income-shock percentages are assumptions, not regulatory thresholds. Use reviewed explanatory templates; no credit approval or unsupported safe borrowing amount.

## 11. Stage 7: Streamlit integration

Four main areas: Screen (verified survey inputs, estimated probability, label/limits), Stress (amounts/scenarios/formulas), Explain (global model interpretation and noncausal limits), Model (sources, comparisons, calibration, definition/version). Do not invent personal explanations when only global importance exists.

Use clear English, laptop/mobile layouts, loading/success/error/empty states and actionable missing-model messages. Reuse exact preprocessing/schema/feature order. Never feed monthly income4500 as annual household income code4500. Survey USD household categories and simulator amounts are separate inputs. Simulator currency may default to AUD; no hidden AUD-to-USD or personal-to-household conversion. Cache trusted model loading. Do not record/upload real financial inputs, secrets or identifiable test records; label demos. Never execute arbitrary uploaded joblib/pickle.

## 12. Stage 8: integration, GitHub and deployment

Meaningful tests cover label/special codes, split isolation, training/application schema, probability range, unseen categories, missing inputs, simulator normal/zero/negative/nonfinite cases, scenario arithmetic, missing artifacts and actual UI behavior. Report executed counts. Import success alone does not establish UI acceptance; use browser or Streamlit testing.

Final hosting target: the user's GitHub and Streamlit Community Cloud. Candidate username yixuan502 is an unverified lead; verify login, ownership and existing remotes. Prepare local code, dependencies, README and publishable-file inventory, then proceed within existing publication authorization once account/repository/scope are clear. If owner/repo/visibility is missing, ask once for only those facts. Suggested repo name BNPLGuard; default private until public visibility or instructor access requirements are resolved. Public app does not imply public raw data or test records.

Commit only this project after reviewing diffs. No force-push, remote deletion, history replacement or invented teammate identity. Ignore environments, caches, credentials, .env, Streamlit secrets, personal inputs and identifiable user records. Respect source licenses; provide acquisition/checksum instructions rather than automatically republishing raw/PDF material. Make trusted, versioned model/schema artifacts available to deployment within size limits.

Use available authorized tools; identify necessary OAuth/login/captcha/user actions without asking for plaintext secrets. Account gaps do not block local work. Before deployment check current Streamlit official requirements, Python/dependencies, entrypoint, branch, resources and paths. Record repository URL, commit, entrypoint, Python, live URL and actual checks in deployment.md. Verify unauthenticated public access; do not claim connections or publication without evidence.

## 13. Stage 9: real users, report and video

Use at least three real nondeveloper participants and a structured instrument, following the confirmed rubric. Templates are allowed; invented participants, results, feedback and improvements are not.

Tasks: complete screening, add200 monthly BNPL, interpret buffer change, locate limitations and distinguish ML from formula results. To answer RQ2, use anonymous IDs and fictional cases. Before the simulator, give text/table information and comprehension questions about buffer changes, independent/cumulative shocks, due-date liquidity and model/formula distinctions. After equivalent simulator tasks, use parallel questions with different numbers. Fix questions/scoring in advance; counterbalance order when feasible. Record correct answers, task completion/time, errors, clarity1–5, comments and actual fixes. Separate objective comprehension from satisfaction.

Small samples, order/practice effects and no randomized control preclude strong causal improvement claims. Without pretest/comparator, report task performance and self-reported usefulness only. Before real collection, create empty protocols/templates; no simulated users as evidence.

The final report separately answers RQ1 and RQ2, distinguishing observations, interpretations and untested claims. Cover users/problem, literature, architecture, data/labels, leakage prevention, actual results, simulator, usability, ethics/limits, future work, references and contributions. Limits include US2016 versus current Australia, self-report, cross-sectional design, no real BNPL outcome validation, weights, subgroup differences, privacy, misuse and monthly simplification. Verify current Australian regulatory claims against ASIC/official sources when written; prior dates and RG281 are search leads only. Use real accessible citations, never fabricated DOI or course text. Follow the actual report/video limits; show a running product, three actual contributions, challenges and limitations, not a mockup pretending to be complete.

## 14. Team responsibilities and records

Suggested, not assigned: memberA Data/ML; memberB Finance/Innovation and simulator; memberC Application/UX. All review objectives, labels, report and video. Do not invent the user's role, commits or individual work.

Maintain progress.md (complete/in progress/blocked/next command), risk_register.md (data/leakage/second source/timing/deployment), experiment_log.md (version/config/validation/decision), and truthful contribution/method-change records.

## 15. Conditional second-source and Australian expansion

Only after CFPB stage 3 works, conduct a bounded Kaggle admission audit without delaying core stages4–9. Decide deferred, EDA/demo only, independent experiment or excluded, with evidence. CFPB supports real-survey difficulty classification; Kaggle may support patterns or separate experiments under its own provenance; the simulator supports explicit arithmetic; Australian official context is not external microdata validation.

For Kaggle obtain raw file, publisher card, version, license and available generation method. Separate verified facts, author claims and unknowns. Audit user/transaction grain, repeated users, dates, missingness, anomalies, label share, units and generation clues. Verify default_flag's event/window/timing and whether repayment_delay_days or missed_payments are post-outcome. Without historical evidence do not use them as application-time predictors. Review risk_score, customer_segment and DTI for target derivation. Isolate repeated users; timestamps alone do not justify forecasting, especially when synthetic. EDA/demo must not invent absent expenses or savings. Any independent model gets separate Dummy/LR/RF configurations, splits, artifacts, metrics and model card.

Never merge CFPB and Kaggle by row, similar demographics or arbitrary IDs; fabricate each other's labels; average/vote unvalidated probabilities; or share test sets. They may coexist in product discussion and separately sourced demonstrations. Kaggle is not CFPB external validation, and different-population/different-label AUCs do not establish superiority. Transfer learning/fusion requires a separately justified design outside default scope.

Australian official evidence is for business context and applicability. Only matched, lawful independent Australian microdata with proper evaluation can support an external-validation claim; market statistics and regulation cannot substitute.

## 16. Acceptance and optional explanation assistant

Priority: real labels/leakage controls → reproducible baselines → evaluation/reliability → correct simulator → usable UI → real user research/report → optional expansion. No invented minimum AUC, favorable sample deletion, label switching, test selection or selective reporting. Modest results are reported honestly.

| Stage | Required evidence |
|---|---|
| 1 | Verified root/environment, specification/progress and material gaps |
| 2 | Sources, dictionary, mapping, sample flow and feasibility decision |
| 3 | Dummy/LR artifacts, fixed IDs and actual validation results; test unused |
| 4 | RF/limited search, comparison and frozen feature/calibration/threshold plan |
| 5 | Final test evidence, curves/calibration, importance, stability/subgroups |
| 6 | Independent formulas, scenarios and boundary tests |
| 7 | Working Screen/Stress/Explain/Model application |
| 8 | Reproducible integration, repository and verified public deployment |
| 9 | Real user records, both research questions, course-compliant report/video |

Kaggle/Australian branches must not displace core deliverables. Deployment/user testing may iterate once a working prototype exists; final claims must correspond to the final version.

Only after core deliverables are ready consider a bounded explanation assistant. Prefer reviewed templates driven by already computed buffer/RTI/coverage/scenario differences/model documentation. An optional LLM may rephrase trusted structured results only: no independent arithmetic, changed probabilities, invented personal causes, credit decisions, unsupported limits or income promises. Explain necessity, data flow, API cost and setup before implementation. Paid use or transmission of real personal data requires explicit authorization. Default to fictional/minimized inputs and deterministic fallback when unavailable. Test numeric fidelity, zero income, negative flow, missing values and out-of-scope requests. Do not turn it into open financial advice, RAG or a required core dependency.

## 17. Initial execution scope and current maintenance scope

The original first round required: inspect actual files/root/AGENTS, establish environment, read course PDFs if available, verify CFPB target/features against official materials, produce audit/dictionary/mapping/feasibility, implement preprocessing, actually run Dummy/LR, save artifacts/schema/config/hashes/validation and update progress/reproduction commands. Stop at stage 3. No Kaggle training, Australian expansion, large search, complete webpage or LLM. Missing files/access must be named precisely while unaffected work continues; never fabricate data or training.

Stages 1–3 have now been completed. The current explicit task is English conversion and desktop migration verification, preserving results, registering the supplied Kaggle file where actually available and rebuilding only the relocated environment as needed. Do not restart the project, redownload available data, retrain merely for translation, or begin stage 4 during this maintenance task.

## 18. Continuation and handoff

At each start read AGENTS.md, progress.md and relevant code. Update this specification and the experiment log for methodological changes. A later generic continue request resumes the next incomplete core stage unless the user sets a narrower scope. Report actual completion, key files, commands/exit status/results, financial/method explanations, limitations and next executable action. Do not repeat the entire plan or paste every file. Keep code, artifacts, report and deployment versions aligned; clearly distinguish demos, placeholders and measured results. Never improve reported performance through test tuning, selective exclusions or changing the objective.

## Authorized stage 4 continuation (4 November 2026)

The user explicitly authorized CFPB candidate comparison and selection, superseding the prior maintenance-only scope in section17. Reuse the frozen label, eight features, raw file and split IDs. Search four RF settings using five-fold training CV, compare raw and train-only sigmoid-calibrated LR/RF on validation, and apply the predeclared selection rule in config/stage4_search.json. Freeze the exact fitted artifact and threshold0.5 for stage5; no refit on train+validation, test evaluation or threshold search in this round. No Kaggle modeling, Australian expansion, app or LLM work. Explanations to the user are Chinese; project files remain English.

## Authorized stage 5 evaluation (4 November 2026)

The user authorized formal locked-test evaluation of the fixed raw LR and prespecified Dummy/raw-RF comparators at0.5, without retraining, recalibration, reselection or feature/label/split changes. The protocol was sealed before scoring. Bootstrap scope, subgroup definitions, validation-only explanation and weighted sensitivity are recorded in config/stage5_evaluation.json and docs/stage5_protocol.md. Stages1–5 are now complete as documented in progress.md; next is stage6. This amendment supersedes obsolete initial/maintenance-only task scopes and test-unopened status descriptions while preserving historical evidence.

## Authorized stage 6 implementation (4 November 2026)

The user authorized the independent monthly financial simulator only. Required five scenarios include current, added BNPL, income shock from current, explicitly combined shock and hypothetical B0 reduction. Validate all six finite nonnegative monetary inputs, income-drop fraction0..1 and reduction0..B0; retain zero-income/zero-outflow results with explained ratio N/A. Return independent metrics/deltas/assumptions and English rule messages without probability, risk bands or credit decisions. Decimal-string serialization and percentage-point display are documented in simulator_method.md. Stages1–6 are complete according to progress.md; stage7 integration is next but not implemented in this round. Frozen ML/schema/label/split/threshold/evaluation and stage-five limits remain unchanged.

## Authorized Kaggle audit branch (5 November 2026)

The user authorized a bounded local/source-quality and leakage audit after stage 6 and before stage 7, without training or core changes. Audit complete: optionC in data_source_decision.md; defer independent modeling and exclude a Kaggle module from the current application. Unknown primary provenance/units/default timing remain explicit. Two auxiliary audit EDA figures are not market evidence. Continue next with stage 7 rather than an unqualified second-model experiment.


## Authorized second-source and explanation extensions (5 November 2026)

The user now explicitly authorizes independent Kaggle recorded-label classification, frozen CFPB local SHAP, an offline result explainer with an optional disabled LLM adapter, and bounded Australian official context. This supersedes the earlier defer-only branch scope. Preserve core estimators, eight inputs, label/splits/threshold, published evaluations and simulator. No CFPB refit, recalibration, reselection or financial formula change. Kaggle protocol is sealed before training in config/kaggle_experiment.json; dataset, split, artifacts and results remain separate. Notebook is reference-only; do not execute or copy unknown-license code. No live API call, financial-input transmission or deployment is authorized by this adapter-only work.


## Extension completion and next scope (5 November 2026)

The explicitly authorized extension branch is implemented and checked. Independent Kaggle research selected a frozen RF under the sealed rule, with appendix-only display. Actual training-background SHAP and offline structured-result explanations are available for the unchanged CFPB model and simulator. Optional LLM is an injected, disabled, approved-phrasing adapter with mock checks only; no live provider/API work occurred. Australian official context is separate from validation/compliance. Preserve the new experimental freeze and original core. Next scope is stage 7 integration; do not reinterpret appendix results as personal prediction or enable an external provider without specific authorization.


## Authorized stage 7 local application integration (5 November 2026)

Build one English local Streamlit app with Screen/Stress/Explain/Model views using the verified frozen CFPB Pipeline, local SHAP, independent simulator and offline templates. Keep all research artifacts and predictions unchanged. Cache trusted resources only; drafts, submissions and narratives stay in session state. Input changes invalidate old submissions. Preserve prediction if local explanation fails; preserve simulator if the model is unavailable. Read saved evaluation evidence, never train/bootstrap/audit on page startup. Kaggle is report-appendix only; LLM stays disabled and no external API or financial-input logging is permitted. Run interface/regression tests, start the app and separately record actual desktop/narrow browser acceptance. Remote publication is stage 8, outside this round.


## Stage 7 accepted; publication next (5 November 2026)

The local app and separate programmatic/browser acceptance are complete, as recorded in stage7_app.md. All research contracts remain unchanged. Next-stage publication must package this accepted version under explicit repository/hosting scope; local acceptance is not public hosting or real-user research. No LLM activation, score fusion or test-driven model changes.


## Authorized stage 8 publication (5 November 2026)

The user explicitly authorizes preparing a clean deployment tree, preserving frozen model/data/evaluation/simulator contracts, pushing to yixuan502/BNPLGuard (private by default), deploying app.py on Streamlit Community Cloud and making the application publicly usable without login. Repository and app visibility are separate. Course PDFs allow a private repository with instructor access; no public-code visibility change is required. Keep secrets, raw data, local environments, per-record predictions, course files and backups out of the release. Python 3.13 and uv.lock define the effective Cloud environment while original requirements remain historical locked evidence. Any required login/OAuth/terms interaction is for the user; never request passwords/tokens in chat. Record actual public acceptance separately from local/clean-tree checks.


## Authorized complete-project GitHub handoff and feedback processing (5 November 2026)

The user now requests the complete project on the existing GitHub repository. Extend the prior deployment-only repository with reviewed source, final research evidence, frozen comparator/Kaggle artifacts, handoff navigation and blank user-study materials. Preserve the private visibility and existing history; do not force-push. The inference runtime allowlist remains separate and unchanged. Raw-source acquisition instructions replace uncertain-license redistribution; environments, obsolete copies, credentials, course PDFs, reference Notebook code, per-record predictions/bootstrap arrays and actual participant workbooks stay local. Only the aggregate feedback review may be committed. This scope supersedes the earlier deployment-only file subset, not any frozen research or privacy contract. No retraining or manual redeployment is authorized/necessary for this publication.
