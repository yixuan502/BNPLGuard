# Model card: BNPLGuard frozen survey-difficulty LR

Status: stage 5 formally evaluated;4 November2026. This is a research screening prototype, not a credit decision policy.

## Intended use and population

Estimate contemporaneous self-reported typical-month difficulty covering expenses and paying all bills, among the2016 US CFPB National Financial Well-Being Survey public-use respondents. Intended for exploratory financial-vulnerability analysis by product/risk teams. It does not predict BNPL default, future hardship, causal effects or validated Australian outcomes. Application/user-study evidence is still pending.

## Frozen object and provenance

Contract: config/stage5_frozen.json. Artifact: models/cfpb/stage4_v1/logistic_regression.joblib, SHA2566f8a82a70e38ae9d5f6143ca4b491d21932d480ca1b38e3d93f079c6794c06d8. This is the unchanged stage-three trained LR retained by stage-four selection. No calibration, retraining or threshold change followed test access. Historical training manifests are preserved; the stage-five evaluation manifest separately records formal test access.

CFPB6394x217, releaseSeptember2017;44 unanswered ENDSMEET labels excluded,6350 eligible. Label1→0;2/3→1. Fixed seed42 split:3810train/1270validation/1270test. No repeated ID or identified household-group overlap. Raw CSV SHA2563680d33576549a99a8dfd7f99d5661a36a8fc1aac0d66f2bf2ec5524695304d8. Local selected-field frequencies match the Codebook; complete byte identity to the current server is unverified. Unused PCTLT200FPL remains excluded due to its47-record frequency discrepancy.

## Inputs and learning

PPINCIMP, SAVINGSRANGES, EMPLOY, VOLATILITY, EARNERS, HOUSING, PRODHAVE_8, PPHHSIZE. All categorical. The persisted codebook/schema checks raw codes; selected special codes become missing, EMPLOY4–8 are collapsed, training-set modes impute missing values and training-fitted one-hot encoding precedes LR(C=1,lbfgs,max_iter1000,random_state42). Survey weights, IDs, age, sex, ethnicity and overlapping hardship questions are excluded as predictors. Employment and socioeconomic attributes can still act as sensitive proxies. All preprocessing statistics were rechecked against training data only.

## Evaluation

Threshold0.5, a fixed reference with no optimized business costs. Test n1270, positives491/negatives779, prevalence38.6614%. The main analysis is unweighted; RF and Dummy are prespecified comparators and cannot reopen selection.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | AP | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression (frozen) | 0.766142 | 0.723502 | 0.639511 | 0.678919 | 0.843158 | 0.763422 | 0.157295 |
| Dummy (prespecified) | 0.613386 | N/A | 0.000000 | 0.000000 | 0.500000 | 0.386614 | 0.237144 |
| Random Forest (prespecified) | 0.762205 | 0.732187 | 0.606925 | 0.663697 | 0.836302 | 0.766896 | 0.166682 |

Selected LR95% respondent-bootstrap intervals: AP[.725172,.802343], AUC[.821062,.864214], Brier[.145968,.168581], Recall[.596038,.681633], F1[.643457,.712873]. Two thousand ordinary iid draws, seed20261104, paired across models. These cover conditional fixed-model/empirical-sample uncertainty, not training/search uncertainty, complex-survey design or transportability. Dummy precision/CI are N/A because it predicts no positives.

RF has slightly higher test AP, but paired LR-minus-RF AP interval[-.015864,.009062] spans zero. LR-minus-RF Brier interval[-.014105,-.004594] favors lower LR squared probability error under this method. Model selection remains unchanged. Validation LR AP=.720857/AUC=.816946/Brier=.167396; there is no descriptive test decline. See stage5_evaluation.md for complete intervals, paired differences and validation/test deltas.

## Reliability and explanation

Mean test LR probability=.401084 versus observed .386614. Ten equal-width calibration bins have n62–220; some show local overestimation, especially .1–.2 and .7–.8. Wilson bin intervals are descriptive and unadjusted. Lower Brier does not certify calibration; absence of extra calibration does not imply failure. No recalibration was fitted.

Validation-only original-column permutation importance(AP,30 repeats) is dominated by savings(mean drop.208307,SD.014293), then household income(.029354,.008613) and household size(.012428,.004377). These are global predictive associations, not individual causes. Correlation and unrealistic shuffled combinations limit interpretation. Stage-four development stability was reused; CV fold SD is not an inferential interval.

## Subgroups, weights and limitations

Prespecified age and income groups show material error differences: LR recall18–34=.7800 versus62+=.4583; underUSD30000 FPR=.5909 versusUSD75000+ .0349. These are descriptive conditional rates with different outcome prevalence/input distributions; they do not establish absence of bias or a causal discrimination finding. Detailed18–24(n75) and70–74(n98,29positives) are small. Group counts, Wilson recall/FPR intervals and all comparator results are saved. No group thresholds were changed.

Primary fit/evaluation is unweighted. finalwt-weighted sensitivity yields LR AP=.789274/AUC=.839151/Brier=.163092 at weighted positive share.430673. These are sensitivity point estimates, not full survey-design inference or population CI. Self-report, cross-sectional measurement,2016 context, liquidity missingness18.52%, employment/wealth proxies and external population mismatch remain limits. At0.5 the LR still misses177 positives and flags120 negatives.

## Engineering and release status

24 tests pass, including saved-model input/schema/missingness/range/repeatability checks and statistical/accounting validation. Use only trusted local model artifacts and the recorded dependency versions. Do not execute unknown uploaded pickles or record real personal inputs. Detailed evidence: outputs/evaluation/stage5_v1; protocol: docs/stage5_protocol.md. No app, deployment, user research or final course report/video is claimed complete. Next stage is the independent deterministic BNPL cash-flow simulator.
