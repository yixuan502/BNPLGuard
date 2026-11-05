# Deployment

Public application: [BNPLGuard](https://bnplguard-yixuan502.streamlit.app/). Public source: [yixuan502/BNPLGuard](https://github.com/yixuan502/BNPLGuard), branch `main`, entry point `app.py`.

The accepted application source is `a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67`, release marker `stress-installments-20261105`. Anonymous acceptance on 5 November 2026 exercised Screen/SHAP/templates, the five standard Stress buffers, instalment examples, invalidation/reset, Explain and saved Model metrics. A 390 x 844 viewport check was browser emulation. Later participant-reported devices are separately documented in the anonymous user-evaluation summary. Documentation/package updates do not establish a new live-browser acceptance.

Streamlit Community Cloud uses Python **3.13** and resolves dependencies from `uv.lock`. No secrets or external AI API are required. The saved model, schema, fixed encoded SHAP reference and aggregate Model evidence must be deployed together. The model is not retrained at startup.

From the project root:

```bash
uv sync --frozen --group test
uv run --frozen python -m streamlit run app.py
uv run --frozen --group test python deployment/smoke.py
```

The reviewed runtime file list is `deployment/runtime_files.json`; the broader source/evidence submission list is `deployment/repository_files.json`. `python -m src.deployment build --output /path/to/new-runtime-package` copies exactly the runtime list and verifies frozen hashes. Use a new output directory; preserve completed research outputs. Raw CSVs and private participant files are unnecessary for inference and are excluded.

Application code retains inputs/results per session and does not log financial inputs or transmit them to an external AI service. CORS/XSRF protections and disabled telemetry remain configured. Hosting-provider behavior is distinct from application code. Community Cloud may sleep or cold-start; confirm public availability before recording or demonstrating the app.
