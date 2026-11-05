# Model and application risks

| Risk | Evidence or consequence | Design control and remaining limit |
|---|---|---|
| Outcome misinterpretation | CFPB ENDSMEET is contemporaneous self-reported difficulty | Label and UI explicitly distinguish it from future BNPL default, credit approval and Australian validation |
| Feature/target overlap | Related hardship scales could restate the outcome | Eight-field schema excludes outcome-like items, IDs and weights; concurrent association is not causality |
| Missingness and proxies | Savings special missingness is 18.52%; resource/employment variables may proxy sensitive attributes | Training-only imputation, documented coding and subgroup diagnostics; no fairness certification |
| Probability and subgroup reliability | LR locally overestimates probability; under-USD30,000 FPR 0.5909 and age-62+ recall 0.4583 | Retain diagnostics, group counts and uncertainty; no post-test threshold/calibration changes |
| Sampling and domain shift | Unweighted 2016 US survey differs from current Australian consumers | Label sample-level metrics, separate weight sensitivity and limit transportability claims |
| Test reuse | Model selection can overfit held-out evidence | Frozen artifacts, split IDs, threshold and predeclared comparisons; no reselection from test scores |
| Uncertainty coverage | Fixed-model row bootstrap excludes fitting, selection and complex-design uncertainty | State conditional interpretation and avoid population/fairness guarantees |
| Source identity | No official byte-level checksum; one unused Codebook-frequency discrepancy remains | Freeze local source hash and schema; preserve version differences and exclude the unresolved field |
| Kaggle provenance/timing | Default definition/window, units and feature availability remain uncertain | Independent exploratory experiment only; exclude post-outcome fields, no probability fusion or personal endpoint |
| SHAP interpretation | Independent masking can break dependence; background affects contributions | Fixed training-only reference, log-odds units, additivity checks and explicit noncausal interpretation |
| Double counting and currency | Financial inputs can overlap or use incompatible units | Separate monthly fields, one currency, explicit expense/repayment boundaries and no implicit survey mapping |
| Monthly timing and contracts | Positive monthly buffer can coexist with due-date shortfalls | Display monthly assumptions; no dated liquidity guarantee or permission to alter repayments |
| Undefined ratios | Zero income/outflows invalidate some ratios | Preserve valid buffer values and show explained N/A ratios |
| Data privacy and artifacts | Personal inputs and untrusted model uploads could create exposure | Session-only application state, no financial-input logging/external LLM call, trusted local artifacts only |
| User-evaluation interpretation | Small samples, prompted tasks, order/practice effects and incomplete original answers | Distinguish independent/assisted results; no causal improvement or universal-success claim |
| Mobile usability | Retest reports scrolling and discoverability/field-confusion issues | Retain observed limitations; broader independent testing is needed |
| Hosting/dependency compatibility | Cloud sleep/cold-start and library changes can affect availability | Python 3.13 lock, portable smoke test and versioned frozen artifacts |

The optional LLM adapter is disabled and has not been live-tested. Offline templates preserve trusted numerical facts. Source attribution, applicable regulatory context and responsible-use limitations are documented separately; successful deployment is not a compliance certification.
