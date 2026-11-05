# Stage 8: public deployment and acceptance

Completed 5 November 2026 (Australia/Sydney). Public application: **https://bnplguard-yixuan502.streamlit.app/**. A fresh browser without Community Cloud login opened the real URL and completed the four-area workflow. This is a working research demonstration, not a real-user study.

## Release identity

- Private source repository: https://github.com/yixuan502/BNPLGuard . Verified owner: yixuan502. No previous local Git history existed; no history was replaced.
- Branch: main; entry point: app.py; Cloud Python setting: **3.13** (explicitly selected instead of the current platform default 3.14); no secrets.
- Initially accepted deployed revision: **c23178cd823ae6d70b4f2cfdb11576bad6793670**. Initial package commit ffa92490dcf1c38793afe7d6313ae02beddc63e5 was independently cloned and tested. The final publication record/screenshots are a subsequent documentation-only commit on main; no numerical runtime module/model changes were needed after c23178c.
- Application Sharing was changed from specific viewers to **This app is public and searchable**. The GitHub repository remains private. Source access for the instructor must be granted separately if required; the course permits public code or instructor access.

## Actual build and environment

Cloud logs show cloning main, successful dependency installation from **/mount/src/bnplguard/uv.lock using uv-sync**, and server startup. The recorded log starts 4 November 2026 at 23:34:51 UTC (5 November 10:34:51 AEDT); dependencies completed at 23:35:04 UTC. Installed core versions include scikit-learn 1.9.1, NumPy 2.5.4, pandas 3.1.0, SHAP 0.54.1, Streamlit 1.66.1 and Altair 6.3.0. Cloud also manages its own pip/certifi and adds watchdog; no core ML package was silently upgraded.

The build reports multiple dependency files and explicitly selects uv.lock. Historical requirements files remain preserved model-environment evidence; this warning did not prevent installation. The server logs 127.0.0.1:8501, and the actual public HTTPS/WebSocket workflow works with the platform proxy. No network-protection change was required. Initial provisioning showed a loading page; the separate anonymous browser subsequently loaded and submitted successfully. The owner management page supplied build/settings evidence and was not used as proof of anonymous app access.

A raw-data-free isolated tree and an actual fresh GitHub clone each installed their own locked .venv and passed all four AppTest areas. First-run checks took 72.488/81.745 seconds including dependency/font-cache initialization; the portable smoke timeout is 120 seconds. The existing project .venv is Python 3.13.13. All 154 local tests passed in 6.41 seconds, and the mandated local audit passed. Startup never trains, bootstraps, recalibrates or regenerates the fixed background.

## Anonymous browser acceptance actually performed

The owner used Chrome to log in to Community Cloud. A separate in-app browser received no Cloud login/OAuth interaction and opened a new tab at the public URL. No login prompt, viewer invitation or owner Manage app control appeared. A second new viewer tab also opened directly with blank inputs and no prior prediction, confirming fresh-session behavior.

| Area | Observed result |
|---|---|
| Screen | Initial empty state; loaded an explicitly fictional questionnaire and submitted. Frozen probability **83.85%**, class 1 at fixed threshold 0.5. Eight original-input SHAP bars and the existing English template corresponded to those choices. |
| SHAP details | Fixed 200 training rows, seed 20261105, log-odds. Encoded additivity error **6.661338147750939e-16**, raw aggregation error **2.220446049250313e-16**, grouping error **4.440892098500626e-16**, probability reconstruction error **1.1102230246251565e-16**. |
| Stress | Loaded fictional I4500/E2500/D700/B0400/Bnew200/S1000, shock20%, reduction200; submitted. Five signed chart values **900 / 700 / 0 / -200 / 1100 AUD**. Current RTI24.44%, coverage0.278 months. Combined template reports -200 AUD, delta -1100 AUD, RTI36.11%, coverage0.263 months with a negative-buffer notice. |
| Explain | Global saved validation Permutation Importance loaded. Local retained the same submitted 83.85% estimate/SHAP. Scenario displayed the submitted five-scenario calculation and its assumptions. |
| Model | Saved AP **0.7634**, ROC-AUC **0.8432**, Brier **0.1573** loaded. ROC and PR views, reliability graph/bin explanation, subgroup/weight disclosures, Kaggle appendix-only decision and dated official Australian links were inspected. Local overestimation and subgroup limitations remain visible. |

The helper is an offline rule template; **LLM remains disabled, not live-tested**. Kaggle has no personal-input endpoint and contributes no probability to screening. Currency/Codebook separation, non-causal explanation and monthly due-date limitations remain.

Screenshots and raw UI/log receipts are saved locally in outputs/deploy/stage8_v1. Only the fictional/aggregate Model screenshot is added to docs/images/app_public.jpg. No real financial inputs, login cookies, credentials or unrelated account material are committed.

## Preservation and release boundaries

All **192** pre-stage-eight protected model/data/config/evaluation/core files remain SHA256-identical. The LR model SHA256 remains 6f8a82a70e38ae9d5f6143ca4b491d21932d480ca1b38e3d93f079c6794c06d8. Eight features, label, fixed splits, 0.5 threshold, calibration choice, saved formal metrics, SHAP reference and simulator results are unchanged. Release packaging uses a default-deny root-anchored allowlist. It excludes raw data, per-record predictions/bootstrap draws, course PDFs, reference Notebooks, backups, local environments, secrets and real-user inputs.

Physical phones, Safari/Firefox, additional networks, adversarial traffic and real-user comprehension were not tested in this remote round. Local stage-seven desktop/mobile emulation and mocked failure tests remain separate historical evidence. Successful checks establish observed availability now; Community Cloud may sleep or cold-start later. Stage-nine real-user feedback has not begun.

## Run and handoff

Send the public app URL above to the instructor; app viewing requires no account in the tested anonymous session. For source review, grant the instructor access to the private GitHub repository through its normal access settings. Do not change repository visibility merely to share the application.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m streamlit run app.py
```

Open the actual printed local URL, normally http://127.0.0.1:8501. Stop that running terminal with Ctrl+C. Do not start a second service on an occupied port or reuse an old PID. PyCharm interpreter: /Users/oneone/Desktop/BNPLGuard/.venv/bin/python; module streamlit; parameters run app.py; working directory the desktop root.

Next: stage-nine real-user feedback, with consent and an explicit protocol, followed by course report/video review and AI-use disclosure. No feedback or student review is invented by this deployment.


## Post-release repository expansion (5 November 2026)

At the user's request the private source repository now includes the reviewed research/team-handoff set, beyond the unchanged99-file inference packaging contract. See deployment/repository_files.json and docs/repository_contents.md. Added study evidence is aggregate only; the received participant workbook remains private.154local regression tests passed in6.27s, the data gate passed and192protected hashes remain unchanged. App source, model, encoded SHAP background, schema, lock and simulator arithmetic are unchanged. Existing Git history/visibility are preserved. This source publication is not a new manual deployment or new anonymous online acceptance; main may refresh automatically through the existing Community Cloud integration. The prior accepted deployed revision is771aadd; use Git history for the newer research handoff revision.
