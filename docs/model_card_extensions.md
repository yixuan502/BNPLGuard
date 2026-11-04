# CFPB model-card extension addendum

5 November 2026. Read together with model_card.md, which remains unchanged to preserve its versioned evaluation evidence. This addendum and the independent kaggle_model_card.md update the project model documentation without altering any frozen estimator or reported metric.

The CFPB model remains raw Logistic Regression, eight inputs, ENDSMEET mapping, training-only fitted Pipeline, locked split and threshold 0.5, with no extra calibration. Local SHAP now explains this exact fitted object in log-odds using a saved 200-row training-only reference. Original-input grouping and sigmoid reconstruction are numerically verified. See cfpb_local_explanation.md.

The tool adds a model-behavior explanation, not validity evidence for a new population/outcome. Global validation Permutation Importance remains distinct and unchanged. Background dependence and independent-masking limitations apply. Contributions are not causal financial causes, recommended interventions or probability percentage points.

Stage-five local probability overestimation and subgroup disparities remain unresolved; bootstrap scope and unweighted primary reporting remain unchanged. SHAP and more fluent explanation do not certify calibration, fairness, BNPL default, future prediction, Australian validity or lending decisions.

The rule-template helper reads verified structured model/simulator outputs separately. No finance formulas or predictions are delegated to language generation. The optional adapter is disabled and not live-tested; it only accepts approved phrasing choices and cannot edit facts or omit limits. No real financial inputs were transmitted. Australian sources provide context only. Kaggle research is an independent appendix with no probability fusion, joins or CFPB validation claim.
