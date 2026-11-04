# Stage 7: accepted local Streamlit application

Completed 5 November 2026. Local URL: http://127.0.0.1:8501 . One app.py entry point; all UI and authored documentation are English.

## Delivered application

| Area | Verified integration |
|---|---|
| Screen | Eight schema/Codebook-derived options with annual household USD, respondent savings, personal work and household scopes. Blank initial state does not score. Missing values require an explicit supported choice. Frozen positive class and threshold 0.5 are retained. A submitted snapshot binds probability, eight-input SHAP and the existing template. Edits invalidate old results; examples/reset are explicit. |
| Stress | Existing simulator and presentation/template interfaces, with no copied financial calculation. Six same-currency amounts, 0–100% shock and bounded hypothetical B0 reduction. Five scenarios, signed chart/zero line, buffer, RTI, coverage and scenario-minus-current deltas. RTI differences use percentage points. Zero-denominator N/A reasons and negative-flow notices remain. |
| Explain | Saved validation Permutation Importance, the current submitted local SHAP and independent monthly formulas/scenarios. Empty Local state does not show another case's explanation. Background/dependence/log-odds/causality limits are expandable. |
| Model | Saved CFPB source/year/label/splits, validation rationale, frozen LR/comparator test results, ROC/PR points, calibration/Wilson bins, bootstrap intervals, subgroup errors and weight sensitivity. No training/evaluation/bootstrap/whole-dataset explanation on startup. |

The app explains contemporaneous US survey difficulty, not BNPL default or credit approval. No risk bands, safe borrowing limits, score fusion or automatic monetary-to-survey mapping were added. Existing local probability overestimation, subgroup differences and population limits remain visible. Kaggle appears only as an expanded report-appendix selection note. Australian sources retain dates/links and are context, not external validation or compliance certification. The assistant is the existing English rule-template helper. LLM is disabled; there is no chat/provider call.

## Code and session behavior

app.py delegates to src/app_ui.py. src/app_inputs.py centralizes real schema choices/scopes and fictional presets; src/app_state.py owns independent session drafts/submission snapshots and restores widget values across navigation. src/app_services.py delegates to the frozen Pipeline, actual FrozenCFPBExplainer and existing simulator/templates. It caches only trusted model/explainer resources (with locks) and static evidence, never personal responses. src/app_charts.py renders saved/structured values without fitting or new statistical evaluation.

Prediction is computed before SHAP. An explanation failure preserves the valid probability and withholds the chart/template; a missing model does not block Stress. Missing evidence produces a clear unavailable state without substitute numbers. Dollar signs in template currency are escaped as literal text rather than Markdown math. Signed axes and zero lines communicate direction independently of color.

.streamlit/config.toml binds to 127.0.0.1, disables telemetry, and retains CORS/XSRF protection. Inputs/results are session-scoped on the local server; no financial-input logging, external API transmission or arbitrary model upload was added. Clearing a section does not overwrite the other section's state.

## Actual acceptance and limits

13 meaningful application tests passed in 5.21s; full regression **151 passed in 5.63s**. CFPB data-audit gate passed and pip check found no broken requirements. All 369 pre-existing captured files and core model-package versions remain unchanged. The fictional simulator response is exactly the accepted prior response, including buffers 900/700/0/-200/1100. No frozen model, feature, label, split, threshold, calibration, formal metric or background selection changed.

AppTest covers exact direct-Pipeline probability/class agreement, SHAP additivity/probability agreement and input binding, template numbers/directions, edits/reset/navigation and separate sessions, zero/N/A/invalid values, controlled missing-model/SHAP/evidence errors, and failure guards against training/bootstrap/background generation/external APIs. Error injection used mocks, not destructive artifact renaming.

Actual Chrome browser acceptance was separate: Screen/Stress/Explain/Model were inspected on desktop and 390×844 phone emulation, with no overall horizontal overflow. Mobile cards stack and text wraps; eight local contributions, signed scenarios and saved model/calibration evidence remain readable. Housing edits visibly removed old prediction/SHAP. Temporary viewport overrides were cleared; a clean empty Screen session remains open. Full browser scope and the distinction from programmatic failures are in outputs/app/stage7_v1/browser_qa.json.

No required local check remains open. Physical devices, Safari/Firefox, remote hosting and real-user comprehension research have not been tested and are not implied. Captures are actual browser output; all submitted personal-looking cases are fictional:

- [Desktop Model](../outputs/app/stage7_v1/desktop_model.jpg)
- [Desktop Explain](../outputs/app/stage7_v1/desktop_explain.jpg)
- [Mobile SHAP](../outputs/app/stage7_v1/mobile_shap.jpg)
- [Mobile Stress](../outputs/app/stage7_v1/mobile_stress.jpg)

## PyCharm and Terminal

Interpreter: /Users/oneone/Desktop/BNPLGuard/.venv/bin/python . Working directory: /Users/oneone/Desktop/BNPLGuard . PyCharm module configuration: streamlit; parameters: run app.py.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m pip install -r requirements-app-lock.txt
.venv/bin/python -m streamlit run app.py
```

Open http://127.0.0.1:8501 . Stop with Ctrl+C in the running terminal. The agent-started demo process ID is in the acceptance receipt; stop that exact current process with kill -INT <recorded_pid>. Do not reuse a stale PID. Stop the existing server before starting a second on port 8501.

```bash
.venv/bin/python -m pytest -q tests/test_app.py
.venv/bin/python -m pytest -q
.venv/bin/python -m src.extensions_verify
```

requirements-app.txt pins Streamlit 1.66.1/Altair 6.3.0 over unchanged core requirements; requirements-app-lock.txt records the complete installed environment.

## Stage 8 conditions

No GitHub push or remote publication occurred. Next confirm repository/branch and hosting permissions, review a deployment allowlist excluding raw datasets/course PDFs/local logs, and package the exact trusted model, schema/label/freeze/split references, fixed SHAP background, fictional presets and aggregate evidence. Verify the target platform's Python/wheel compatibility with the lock; apply host-specific network settings while retaining disabled LLM/telemetry. Then publish under explicit next-stage scope and verify the real HTTPS/WebSocket URL and four areas/session/error behavior. Public-hosting and real-user/course-report acceptance remain separate later work.
