# Feature selection and leakage review

The feature set was fixed before fitting, using the Codebook, instrument and financial rationale. No test performance or full-sample target correlations were used to select inputs.

| Field or group | Decision | Rationale |
|---|---|---|
| PPINCIMP | Retain as categorical | Annual household USD income range; not an exact amount or a direct mapping from monthly AUD income |
| SAVINGSRANGES | Retain as categorical | Cash/checking/savings liquidity; legitimate contemporaneous association, not a deterministic target transformation |
| EMPLOY | Retain after grouping | Keep codes 1/2/3; combine 4–8 into 4; 99 is missing. Removes separate disability/retirement indicators, but age and health proxy risks remain |
| VOLATILITY | Retain | Income stability rather than ability to pay bills |
| EARNERS | Retain | Number contributing income toward household bills, distinct from household size |
| HOUSING | Retain | Ownership/rental context, without inferring mortgage balance |
| PRODHAVE_8 | Retain | Current education-loan product, with no delinquency outcome or amount |
| PPHHSIZE | Retain as categorical | Household size is top-coded at 5+; code 5 is not exactly five people |
| ENDSMEET and its derivatives | Exclude | The target and deterministic transformations are direct leakage |
| FWBscore, FWB1_*, FWB2_* | Exclude | Overlapping concepts such as bill arrears and money left at month end. FWBscore uses its own ten items; it is not claimed to directly contain ENDSMEET |
| MATHARDSHIP_*, COLLECT, COVERCOSTS | Exclude | Concurrent/past hardship and coping actions may restate the answer; not all are mathematical target leakage |
| ABSORBSHOCK | Exclude from baseline | Subjective emergency-financing difficulty overlaps the target; concrete savings bands are retained instead |
| PUF_ID | Split key only | No business input meaning |
| sample, finalwt | Sampling/sensitivity only | Never ordinary model predictors |
| agecat, generation, PPETHM, PPGENDER and similar attributes | Exclude from predictors | Reserve for subgroup audits; do not add protected attributes merely to increase scores |
| HOUSERANGES, IMPUTATION_FLAG | Exclude from baseline | Official recontact and imputation introduce additional interpretation complexity |
| PCTLT200FPL | Exclude and register issue | Local marginal frequencies differ from the Codebook |
| Every other column | Exclude by default | The allowlist contains only the eight approved inputs |

There is no prospective application-time design. Savings depletion may be a consequence of difficulty, so changing savings cannot be claimed to causally change risk. Inputs are voluntary self-reports. The complete Pipeline stores the schema and rejects illegal codes such as savings=4500. OneHotEncoder's unknown-category protection covers valid categories absent from training; it does not replace input validation.

The application is not built. The schema is a future UI contract, not completed questionnaire acceptance. Original panel question wording for PPINCIMP and PPHHSIZE is absent from the survey appendix; field labels and proposed prompts are distinguished from original questions. An unchecked education-loan item does not establish verified absence of debt.
