# BNPLGuard

**AI-Powered Financial Vulnerability Screening and BNPL Repayment Stress Simulation**

[Public application](https://bnplguard-yixuan502.streamlit.app/) | [Source repository](https://github.com/yixuan502/BNPLGuard)

BNPLGuard is a financial research prototype with four areas: **Screen**, **Stress**, **Explain** and **Model**. It combines a frozen Logistic Regression model for US survey financial difficulty with an independent BNPL cash-flow simulator. The application uses offline English explanation templates. The optional LLM adapter is disabled and has not been live-tested; no API key is required.

## Installation

Use Python **3.13**. From the repository root, install the locked environment and start Streamlit:

```bash
uv sync --frozen --group test
uv run --frozen python -m streamlit run app.py
```

Alternatively, create `.venv` with Python 3.13, install `requirements-app-lock.txt`, and run `.venv/bin/python -m streamlit run app.py` (Windows: `.venv\Scripts\python.exe -m streamlit run app.py`). In PyCharm, select that interpreter, use the directory containing `app.py` as the working directory, and run module `streamlit` with arguments `run app.py`.

Open the address printed by Streamlit, normally <http://127.0.0.1:8501>. Stop with Ctrl+C. Use `--server.port 8502` if a different port is needed. Community Cloud uses `uv.lock`; dependencies must remain compatible with the saved model. The application does not train or evaluate models on startup.

## Features and worked examples

- **Screen:** Select eight CFPB survey categories and submit. The fictional example returns **83.85%** for the specified survey difficulty label. Annual household USD bands are separate from the simulator's monthly amounts. Editing inputs invalidates the previous estimate; reset clears the section.
- **Stress:** Enter monthly after-tax income, living expenses, other debt repayments, existing BNPL, proposed BNPL and available savings in one currency. Living expenses exclude repayments entered separately. Five visible cards compare current, added BNPL, income shock, both changes, and a hypothetical reduction in existing BNPL.
- **Monthly instalment estimate:** Optionally enter purchase amount, upfront payment and a positive number of monthly instalments. Review the cent-exact allocation, then apply the highest monthly instalment to Stress. The estimate assumes no fees or interest and an upfront payment before the simulated month; savings are the remaining balance. It is not a provider quote.
- **Explain:** Inspect global validation-set permutation importance, submitted-input SHAP contributions and independent scenario formulas. SHAP units are log-odds, not probability percentage points or causal effects.
- **Model:** Inspect data sources, label/split definitions, model comparisons, held-out metrics, ROC/PR curves, calibration, subgroup differences and limitations.

The fictional Stress example uses AUD 4,500 income, 2,500 living expenses, 700 other debt, 400 existing BNPL, 200 proposed BNPL and 1,000 savings, a 20% income shock and a hypothetical 200 reduction. The five monthly buffers are **900 / 700 / 0 / -200 / 1,100 AUD**. Savings are not monthly income. Positive monthly cash flow does not guarantee cash on every due date; a hypothetical repayment reduction does not change a contract.

![Application Model page](docs/images/app_public.jpg)

## Model and evaluation

CFPB's 2016 US National Financial Well-Being Survey has 6,394 rows and 217 columns. Excluding 44 missing labels leaves 6,350 respondents and 2,454 positives. ENDSMEET responses 2/3 map to difficulty (1); response 1 maps to no difficulty (0). The eight categorical inputs, train/validation/test split of 3,810/1,270/1,270, threshold 0.5 and uncalibrated LR artifact are frozen.

| Held-out test model | AP | ROC-AUC | Brier |
|---|---:|---:|---:|
| Dummy | 0.386614 | 0.500000 | 0.237144 |
| Logistic Regression (selected on validation) | 0.763422 | 0.843158 | 0.157295 |
| Random Forest | 0.766896 | 0.836302 | 0.166682 |

These are unweighted test-sample results (n=1,270). Test scores were not used to reselect the model. The model identifies contemporaneous self-reported difficulty; it is not future BNPL default prediction, credit approval or Australian external validation. Local probability overestimation, subgroup error differences, imputation and domain limits remain. Simulator arithmetic does not change the model estimate. The independent Kaggle recorded-label experiment is exploratory research only, with provenance, timing and unit limitations; it is excluded from personal screening.

## User evaluation

Structured user-evaluation records cover an initial three-participant study and an updated-app retest with two new participants and one returning participant. First-round recorded app answers include prompted responses. The retest also records prompts for some tasks, mobile scrolling and discoverability issues, and unresolved timing of one participant's savings hesitation. Neither study establishes causal improvement or universal independent completion. Feedback summaries are paraphrases rather than verified quotations.

See the [initial study](docs/user_testing_feedback_review.md), [updated-app evaluation](docs/retest_evidence_2026-11-06.md), and [structured test instruments](user_testing/materials_v1/participant_test_sheet.pdf). Original participant workbooks and identifying metadata are not included.

## Verification and data access

```bash
uv run --frozen --group test python -m pytest -q
uv run --frozen --group test python deployment/smoke.py
```

The smoke test runs all four application areas without raw CSVs. The included tests validate portable application behavior, frozen inference, explanations, formulas, input/failure handling and saved aggregate evidence. Checks that require the original raw-data and whole-development archive are held separately with that archive. Passing the submission suite does not imply that the excluded historical research archive was reproduced.

Frozen model/schema/background bytes and saved aggregate evaluation evidence are included. Raw data, private participant records, development archives and local environments are excluded from the submission file lists. See [data sources and reproducibility](docs/data_sources.md), [architecture](docs/architecture.md), [deployment](docs/deployment.md) and the reviewed manifests in `deployment/`.

## Known limitations and future work

Potential improvements include clearer separation of existing/proposed repayments, more discoverable purchase-plan input, reduced phone scrolling, larger independent user studies, and external validation before any population or lending claim. A dated repayment calendar, fees/interest and multi-month depletion are not implemented. Community Cloud may sleep or cold-start; check the public app before a demonstration. No paid API, arbitrary model upload, real-time data feed or enabled chatbot is provided.

## Security and attribution

The app loads only trusted local artifacts, retains inputs/results in session state and does not log financial inputs or send them to an external AI API. No secret is required or committed. Any future API integration must use environment variables or platform secrets rather than hardcoded credentials.

Codex assisted with data/schema audits, implementation, model experiments and evaluation, SHAP, simulation, application/deployment checks and documentation. The submitting team is responsible for understanding and reviewing the work and accurately disclosing assistance and actual individual contributions in the assessed report.

Technical methods and source attribution are recorded in the model cards, data dictionaries, leakage reviews and source records under `docs/` and `data/metadata/`. The Kaggle dataset page screenshot states CC0 1.0; this is separate from the unconfirmed reference Notebook code license. No new open-source code license is assigned here.
