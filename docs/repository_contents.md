# Complete-project repository contents

The private repository preserves its existing Git history and adds the reviewed research/handoff file set to the earlier deployment-only subset. `deployment/repository_files.json` is the explicit repository publication list; `deployment/runtime_files.json` remains the unchanged inference-only packaging contract. Adding research files does not authorize training on startup. The application source, dependencies, frozen model, SHAP background, numerical results and simulator are unchanged from the accepted release.

Included: current Python source and tests; experiment/schema/freeze configs; exact dependency locks; stage-four frozen models/comparators; independent Kaggle models and aggregate results; aggregate formal metrics, intervals and plots; simulator and fictional SHAP examples; model cards, audit/source/method records; original deployment receipts; three team navigation documents; blank English participant/facilitator instruments and their authoring sources; an aggregate feedback verification note. Historical receipts retain their original timestamps/status fields; later completion evidence supersedes stale pending fields, as documented in EVIDENCE_MAP.

Excluded: `.git`, virtual environments, caches, obsolete copied checkouts/backups, secrets, actual participant workbooks, personal author/path metadata, user-input logs, row-level predictions and bootstrap arrays. Raw CSVs, unknown-license reference Notebook code, and restricted course PDFs are not automatically redistributed. Their absence does not affect app inference; it does affect original research audits/training/evaluation and some historical tests. This is a complete reviewed project handoff, not a byte-for-byte backup of the development computer. No fresh-environment full research rerun is claimed.

## Acquire omitted source materials

1. CFPB: https://www.consumerfinance.gov/data-research/financial-well-being-survey-data/ . Obtain the September2017 public-use CSV for the2016 survey, save as `data/raw/cfpb/NFWBS_PUF_2016_data.csv`. Expected6394rows/217columns; local SHA256 `3680d33576549a99a8dfd7f99d5661a36a8fc1aac0d66f2bf2ec5524695304d8`. The official download may change: preserve a different version separately; never silently replace frozen data. Existing Codebook/User Guide are included as official source documents. See `data/metadata/source_manifest.json` for source and byte-identity limits. Raw data is needed for the research audit and original fold/row tests, not the deployed screen.
2. Kaggle: https://www.kaggle.com/datasets/shree0910/buy-now-and-pay-later-fintech-ml-dataset . After checking the current dataset terms/version and any login requirement, save `data/raw/kaggle_bnpl/Buy_Now_Pay_Later_BNPL_CreditRisk_Dataset.csv`. Expected10345rows/17columns; SHA256 `780cdb1eec43519b0764059563d89258ef1d9e4cef3b1ffdeab9622d6976b1bd`. Screenshots state CC0 1.0; authenticity, label/timing/currency limits remain unresolved. Needed only for independent audit/experiment reproduction, never CFPB validation or app personal screening.
3. Notebook: https://www.kaggle.com/code/sumedh1507/bnpl-credit-risk-insights . Optional `notebooks/reference/bnpl-credit-risk-insights.ipynb`; code license is not established. Review is included; no copied external implementation or results underpin our metrics.
4. Course PDFs: obtain `project-a-tech-team.pdf` and `marking-criteria-a-tech-team.pdf` from the official FINS5557 Moodle TrackA course area, then place under `docs/references/`. Check project briefp3 and rubricp4 for the minimum-three-user requirement; consult current originals for all formal obligations. These files are required for course-compliance review, not application startup. They are not republished without permission.

Raw acquisition alone does not restore every excluded historical row-level receipt; original whole-archive hash-preservation tests are archival checks. On a clean Git checkout use the app smoke and packaging checks below. The retained desktop research archive supports the full original test suite; do not silently regenerate frozen predictions or official evaluation to make tests pass.

## Run and check

```bash
uv sync --frozen --group test
uv run --frozen python -m streamlit run app.py
uv run --frozen --group test python deployment/smoke.py
uv run --frozen --group test python -m pytest -q tests/test_deployment.py
```

Use Python3.13. See README for the project .venv/PyCharm workflow. LLM remains off. Repository visibility is private; the public app is https://bnplguard-yixuan502.streamlit.app/ . This publication does not itself re-run anonymous Cloud acceptance; historical verified release is771aadd. Community Cloud may automatically refresh from main; no manual deployment or configuration change is made here.

## Feedback custody

`user_testing/materials_v1/anonymous_results.xlsx` is the unchanged blank instrument. Received participant workbooks live only in ignored `user_testing/private/`; the original includes author/path metadata and must not be committed. `outputs/user_testing/feedback_review_v1/review.json` and `docs/user_testing_feedback_review.md` contain aggregate findings and limitations, not raw identifiable records. Recruitment/consent fields are source statements, not independently authenticated attendance.
