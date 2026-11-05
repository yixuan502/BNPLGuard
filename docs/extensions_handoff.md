# Verified extension handoff for Streamlit

Completed 5 November 2026. No Streamlit implementation or deployment was added. Read this with the experiment/model cards and progress record.

| Interface | Status | Integration contract |
|---|---|---|
| extension_service.predict_and_explain_cfpb(codes) | Verified actual frozen LR + SHAP | Exactly eight survey code fields, never mapped from monetary sliders; returns ok or invalid_input; cache explainer per app process |
| extension_service.simulate_and_explain(amounts, income_drop, bnpl_reduction) | Verified existing independent simulator + offline text | Six finite nonnegative amounts in one currency; shock fraction 0..1; preserve partial/N/A/errors and all independent scenarios |
| result_explainer.explain_results(cfpb, simulator) | Verified offline templates | Accept trusted valid producer outputs; display financial/model interpretations separately; no rescoring or finance arithmetic |
| llm_adapter.OptionalLLMAdapter | Prepared, not live-tested; disabled | No provider/key/HTTP implementation; authorization gates and approved-phrase-only mock validation/fallback |
| extension_service.load_kaggle_research_summary() | Application-disabled by default | Explicit include_appendix=True reads independent research evidence only; no personal prediction method |

Add Screen/Stress/Explain/Model views around these interfaces next. Display original financial assumptions and model limits before making interpretation claims. Retain stage-five local overestimation/subgroup findings, SHAP log-odds and background dependence, due-date/monthly limits and hypothetical reductions. Kaggle results belong to the report appendix; do not construct an application probability fusion.

PyCharm working directory: /Users/oneone/Desktop/BNPLGuard. Interpreter: /Users/oneone/Desktop/BNPLGuard/.venv/bin/python.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m pip install -r requirements-extensions.txt
.venv/bin/python -m src.extensions_verify
.venv/bin/python -m pytest -q
.venv/bin/python -m src.extension_service --output-dir outputs/extensions/pycharm_demo_01
.venv/bin/python -m src.cfpb_local_explanation --output-dir outputs/explanations/pycharm_01
.venv/bin/python -m src.kaggle_experiment --phase verify
```

Use new output paths for demos; completed runs are protected. Verification does not train or repeat formal test evaluation. A deliberate Kaggle rerun is documented separately in kaggle_experiment.md, always reusing locked IDs and the sealed design.

Acceptance: 23 extension checks and 138 full-suite tests passed. CFPB data-audit gate passed. The 221 preexisting protected files, core dependencies, frozen fixture predictions and simulator response are unchanged. Core model-card/evaluation files remain immutable; model_card_extensions.md is the new companion addendum. Official Australian context is archived separately. No account, API fee or data-transfer permission is needed to run the default functionality.
