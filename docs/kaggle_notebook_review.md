# Reference Notebook review

Reviewed 5 November 2026 without executing the Notebook. Source: notebooks/reference/bnpl-credit-risk-insights.ipynb; SHA256 123a8f63ed40708e2e656d189b6c561ec0d57fa166a034157c2ece291b86b7b0. The supplied Downloads copy is byte-identical. The reference remains unchanged. Cell indices below are zero-based. Saved outputs are the original author's records, not this project's reproduced results.

| Check | Actual evidence | Project treatment |
|---|---|---|
| CSV path | Cells 1, 10 and later reload /kaggle/input/datasets/shree0910/buy-now-and-pay-later-fintech-ml-dataset/Buy_Now_Pay_Later_BNPL_CreditRisk_Dataset.csv | Linkage of name/namespace, not authenticated local-byte identity |
| Version metadata | metadata.kaggle.dataSources includes sourceType=datasetVersion, sourceId=15502327 | Internal source identifier, not a verified publisher version number |
| Target | Cell 0 prints 0=No Default, 1=Default | No specific criterion, obligation, maturity or outcome window established |
| Outcome-like predictors | Cell 10 drops target/risk_score/customer_segment/user_id/date but retains repayment_delay_days and missed_payments | Exclude these and their derivatives from this project's experiment |
| Preprocessing order | Cells 10–12 fit label encoders and StandardScaler before train_test_split; cell 1 also performs full-file median filling | Transductive preprocessing leakage; nominal label encoding imposes order. Our fresh Pipeline is fit inside training folds |
| Engineered variables | Cells 1 and 9 create income_per_installment, delay_ratio, month and high_spend_flag. Cell 10 reloads the raw CSV | Earlier derivatives are not actually used by that main model; no claimed uplift adopted |
| Conclusions | Cells 10, 12, 14 and 16 print fixed performance/business statements; cell 16 names a best model without a computed selection rule | Statements do not establish evidence, safe approvals, real-world savings or causality |
| Code license | No explicit code license found in source/metadata | Data-page CC0 and Notebook-code rights are separate; no unknown-license code was copied |

The metadata identifies Python 3.12.12 and disabled Kaggle internet; these describe the reference environment, not this project's environment. Cell/output hashes, execution counts and clearly labeled author-output excerpts are in docs/references/kaggle_supplement_2026-11-05/notebook_review.json. Other Notebook methods, including ensembles, LIME, clustering and anomalies, are outside this bounded implementation. No external model score was imported.
