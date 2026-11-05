# Data sources and reproducibility

Application inference and the portable test suite use included frozen artifacts and aggregate evidence. They do not require raw CSVs or original participant records. `deployment/repository_files.json` lists submission files; `deployment/runtime_files.json` lists the smaller application package.

## CFPB

Source: [National Financial Well-Being Survey](https://www.consumerfinance.gov/data-research/financial-well-being-survey-data/), 2016 survey public-use data released in September 2017. For deliberate research reproduction, obtain the CSV and save it as `data/raw/cfpb/NFWBS_PUF_2016_data.csv`. Expected shape: 6,394 x 217. Frozen local SHA256: `3680d33576549a99a8dfd7f99d5661a36a8fc1aac0d66f2bf2ec5524695304d8`. Preserve a different source version separately. Acquisition and byte-identity limits are recorded in `data/metadata/source_manifest.json`; official codebook/user-guide PDFs are included as references.

The target, feature schema and split IDs are fixed. Research commands must preserve completed runs and must not tune, refit or recalibrate using test results. `src.data_audit` checks the raw source and regenerates audit tables/dictionary; it is not an application startup step. The archived preflight/whole-history checks additionally require the original research archive and are not equivalent to clean-checkout tests.

## Kaggle

Source: [Buy Now and Pay Later Fintech ML Dataset](https://www.kaggle.com/datasets/shree0910/buy-now-and-pay-later-fintech-ml-dataset). Expected CSV: `data/raw/kaggle_bnpl/Buy_Now_Pay_Later_BNPL_CreditRisk_Dataset.csv`, 10,345 x 17, SHA256 `780cdb1eec43519b0764059563d89258ef1d9e4cef3b1ffdeab9622d6976b1bd`. Verify current access terms/version before acquisition. Screenshots state CC0 1.0; source authenticity, default definition/window, timing, currency and frequency remain incompletely established. This dataset is never joined to CFPB or used as Australian external validation.

The [reference Notebook](https://www.kaggle.com/code/sumedh1507/bnpl-credit-risk-insights) is reviewed in `kaggle_notebook_review.md`; its code license is unconfirmed and its code is not distributed. Saved outputs from that Notebook are not this project's results.

## User evaluation and other references

Blank instruments, verified fictional cases and anonymous study summaries are included. Original participant workbooks, precise session times and identifying metadata are held separately from the project and are not distributed. The study summaries distinguish independent from prompted outcomes and retain unresolved questions. They do not demonstrate model accuracy or causal improvement.

Official Australian context is referenced through `references/australia_2026-11-05/source_register.json` and `australian_context.md`. Publication/access dates and evidential limits are separate. These references provide context rather than external model validation or a compliance certification.

Course materials must be obtained from the official course system; restricted course PDFs, report drafts, team instructions, development environments, duplicate checkouts and historical maintenance logs are not part of this source submission.
