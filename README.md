# BNPLGuard

**AI-Powered Financial Vulnerability Screening and BNPL Repayment Stress Simulation**

[Open the public application](https://bnplguard-yixuan502.streamlit.app/) · [GitHub repository](https://github.com/yixuan502/BNPLGuard)

BNPLGuard is an English-language research prototype with four areas: **Screen**, **Stress**, **Explain** and **Model**. Screen uses a frozen Logistic Regression Pipeline trained on US survey data. Stress independently calculates monthly repayment scenarios. Explain presents saved global importance and local SHAP contributions. Model displays saved evaluation evidence and limitations.

The application uses offline English explanation templates. **The optional LLM adapter is disabled and has not been live-tested.** No API key is required. The independent Kaggle experiment is retained as research material and is not part of personal screening.

## Run locally

Clone or download the repository and open a terminal in the resulting **BNPLGuard project root** (the directory containing `app.py`). Use Python **3.13**. In PyCharm, set the project root as the working directory, select the interpreter inside the project's `.venv`, and run module `streamlit` with parameters `run app.py`.

For a fresh checkout, install [uv](https://docs.astral.sh/uv/getting-started/installation/) and use the committed lock:

```bash
uv sync --frozen --group test
uv run --frozen python -m streamlit run app.py
```

Alternatively, after creating the project virtual environment and installing `requirements-app-lock.txt`:

```bash
# macOS / Linux, from the project root
.venv/bin/python -m streamlit run app.py
```

```powershell
# Windows PowerShell, from the project root
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the address printed by Streamlit, normally <http://127.0.0.1:8501>. Stop the process with **Ctrl+C**. If the port is occupied, use the existing instance or choose another port, for example `--server.port 8502`.

Community Cloud resolves dependencies from `uv.lock`. The locked environment includes scikit-learn 1.9.1, NumPy 2.5.4, SHAP 0.54.1 and Streamlit 1.66.1. Starting the application does not train a model, run an audit or bootstrap the test set.

## Using the application

- **Screen:** Enter eight CFPB survey categories and submit. Annual household income uses USD bands; these inputs are separate from Stress's monthly amounts. The fictional screening example and reset button are available.
- **Stress:** Enter monthly after-tax income, living expenses, non-BNPL debt repayments, existing and proposed BNPL repayments, and the current savings balance in one currency. Living expenses exclude repayments entered separately. Five cards compare current, new BNPL, income shock, both changes, and a hypothetical reduction in existing BNPL. Each displays a final buffer and its change from current.
- **Monthly instalment estimate:** Direct entry of the new monthly repayment is the default. Optionally choose **Estimate from a purchase plan**, enter purchase amount, upfront payment and a positive number of monthly instalments, review the result, and select **Use this repayment in the stress simulator** before comparing scenarios. The first N−1 instalments are rounded down to cents, the last clears the remainder, and the highest monthly instalment is applied. The estimate assumes monthly payments, no interest or fees, and an upfront payment made before the simulated month. Savings are the balance after that payment. This is not a provider quote. See [instalment method](docs/installment_plan.md) for validation rules and limitations.
- **Explain / Model:** Review validation-set Permutation Importance, the submitted input's SHAP contribution, and saved test metrics, curves, reliability and subgroup results. No model is retrained when these pages open.

The standard fictional Stress example uses AUD 4,500 income, 2,500 living expenses, 700 other debt, 400 existing BNPL, 200 proposed BNPL and 1,000 savings, with a 20% income shock and a hypothetical 200 reduction. Its five buffers are **900 / 700 / 0 / −200 / 1,100 AUD**. Savings do not count as monthly income. Positive monthly cash flow does not guarantee funds on every payment due date; a hypothetical repayment reduction does not change a contract.

## Research scope and limitations

The CFPB outcome is **contemporaneous self-reported difficulty** covering expenses and paying bills in a typical month, from the 2016 US National Financial Well-Being Survey. ENDSMEET responses 2/3 are mapped to class 1 and response 1 to class 0. The eight categorical inputs, stratified 3,810 / 1,270 / 1,270 split and 0.5 threshold are frozen; no extra calibration is applied.

The selected Logistic Regression's held-out **test** AP is **0.763422**, ROC-AUC **0.843158** and Brier score **0.157295**. These primary metrics are unweighted. The model has local probability overestimation and subgroup error differences; its performance on Australian consumers has not been externally validated. It is not a BNPL default or credit-approval model. Local SHAP contributions use **log-odds**, not probability percentage points, and do not establish causes.

The simulator uses deterministic arithmetic, not model predictions or default probabilities. Changing a Stress input does not alter the Screen estimate. The separately trained Kaggle experiment classifies the dataset's recorded `default_flag` for exploratory research only. Its provenance, outcome definition, timing and financial units have important gaps; it does not validate CFPB or Australian deployment. See the [model card](docs/model_card.md), [explanation addendum](docs/model_card_extensions.md), [Kaggle model card](docs/kaggle_model_card.md) and [data-source decision](docs/data_source_decision.md).

## User-testing evidence

Two rounds have been recorded using structured fictional tasks. In the first-round compilation, 16/18 written answers and 18/18 recorded app answers were correct; the latter includes 12 answers recorded after operational guidance. The original independent app answers for those assisted tasks and complete Screen-interpretation wording are unavailable. See the [first-round evidence review](docs/user_testing_feedback_review.md).

The updated-app retest workbook records three sessions: **two new participants and one returning participant**. Some tasks required prompts, including distinguishing savings from monthly income, identifying repayment fields, finding the purchase-plan option, or stating a change from current. One participant reported substantial scrolling on a phone. The sequence of P01's recorded savings understanding and hesitation cannot be confirmed from the available notes. These small, nonrandomized sessions do not establish a causal improvement or universal independent success. Feedback summaries are not verified verbatim quotations.

Original participant workbooks remain private and are not included in the public repository. The [anonymous updated-app retest summary](docs/retest_evidence_2026-11-06.md) records task-specific independent and prompted outcomes, evidence limitations and remaining usability questions. Do not publish source records or identify participants. The [blank participant materials](user_testing/materials_v1/participant_test_sheet.pdf), [blank retest form](user_testing/retest_v1/retest_form.md) and [facilitator guide](user_testing/retest_v1/facilitator_notes.md) are separate from collected responses.

## Deployment and verification

The [repository](https://github.com/yixuan502/BNPLGuard) is **public** on `main`; its visibility was verified on 6 November 2026. The public app runs on Streamlit Community Cloud. The updated Stress and instalment application code was committed as [`a77bc23`](https://github.com/yixuan502/BNPLGuard/commit/a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67), with release marker `stress-installments-20261105`. A later documentation-only commit records the acceptance.

On 5 November 2026 at 23:39 AEDT, an anonymous browser showed the marker and exercised Screen/SHAP/templates, the standard Stress example, both instalment examples, mode switching, invalidation, reset, Explain and Model. A 390-pixel viewport was also checked; this was browser emulation, distinct from the later participant's reported iPhone session. Local regression recorded **170 tests passed**, followed by **32 relevant tests passed** after adding the release marker. See the [deployment record](docs/deployment.md) and [Stress change record](docs/stress_feedback_changes.md). Community Cloud can sleep or take time to start; repeat a fresh access check before a live demonstration.

The inference file list is maintained in `deployment/runtime_files.json`, and the broader reviewed repository list in `deployment/repository_files.json`. Raw datasets, participant workbooks, local environments, secrets, reference Notebook code and course PDFs are excluded from the release. The app loads only trusted local artifacts; the app code keeps inputs in session state and does not log financial inputs or send them to an external AI API.

From a complete local research copy, run:

```bash
# macOS / Linux: full local archive, including the required source data
.venv/bin/python -m pytest -q
# Audits the reviewed runtime files and frozen hashes
.venv/bin/python -m src.deployment audit
```

A raw-data-free checkout can run `uv run --frozen --group test python deployment/smoke.py`. It cannot reproduce every historical research check without the omitted data and archive artifacts. Source acquisition, expected paths, checksums and limitations are in [repository contents](docs/repository_contents.md).

![Public Model page](docs/images/app_public.jpg)

## Project documentation

- [Current course requirement checklist](docs/rubric_checklist.md) and [anonymous updated-app retest summary](docs/retest_evidence_2026-11-06.md).
- [Project specification](docs/project_spec.md), [progress](docs/progress.md), [experiment log](docs/experiment_log.md) and [model selection](docs/model_selection.md).
- [Simulator method](docs/simulator_method.md), [local SHAP method](docs/cfpb_local_explanation.md), [result templates](docs/result_explainer.md) and [Australian context](docs/australian_context.md).
- [Team introduction](START_HERE.md), [evidence map](EVIDENCE_MAP.md) and [AI handoff prompt](AI_HANDOFF_PROMPT.md). Some historical documents retain their original time-specific status; later acceptance and retest records supersede older pending statements.
- [Contribution and AI-assistance log](docs/contribution_log.md): the team must verify and document each student's actual contribution, review the work and complete the required disclosure.

Dataset licenses and Notebook code licenses are separate. The Kaggle page screenshot states CC0 1.0 for the dataset; the reference Notebook's code license is unconfirmed. No new open-source code license is assigned by this README.
