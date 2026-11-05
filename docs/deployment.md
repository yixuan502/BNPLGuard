# Stage 8: public deployment and acceptance

## Current status - 6 November 2026

The [source repository](https://github.com/yixuan502/BNPLGuard) is public. The [public app](https://bnplguard-yixuan502.streamlit.app/) has accepted release marker `stress-installments-20261105` (application source `a77bc23`). Updated-app structured retest records have been received for three participants: two new and one returning. Read the [anonymous retest summary](retest_evidence_2026-11-06.md) for independent versus prompted outcomes and unresolved questions. Original participant workbooks remain private; the study does not prove causal improvement or universal independent completion.

This current status supersedes earlier private-repository and pending-retest statements below. Earlier stage records retain their original context and are not current completion claims. Final report/video, signed student contributions, AI disclosure and Moodle approval/deadline evidence still require separate verification.

## Historical deployment log

Completed 5 November 2026 (Australia/Sydney). Public application: **https://bnplguard-yixuan502.streamlit.app/**. A fresh browser without Community Cloud login opened the real URL and completed the four-area workflow. This is a working research demonstration, not a real-user study.

## Release identity

- Initially private source repository: https://github.com/yixuan502/BNPLGuard . Verified owner: yixuan502. No previous local Git history existed; no history was replaced.
- Branch: main; entry point: app.py; Cloud Python setting: **3.13** (explicitly selected instead of the current platform default 3.14); no secrets.
- Initially accepted deployed revision: **c23178cd823ae6d70b4f2cfdb11576bad6793670**. Initial package commit ffa92490dcf1c38793afe7d6313ae02beddc63e5 was independently cloned and tested. The final publication record/screenshots are a subsequent documentation-only commit on main; no numerical runtime module/model changes were needed after c23178c.
- Application Sharing was changed from specific viewers to **This app is public and searchable**. At initial deployment, the GitHub repository was private and required separate instructor access. It is now public, as verified on 6 November 2026; the course permits public code or instructor access.

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

Send the public app URL above to the instructor; app viewing requires no account in the tested anonymous session. For source review, use the now-public GitHub repository URL. The original private-source handoff required separate instructor access; that historical instruction is superseded by the visibility verification on 6 November 2026.

```bash
cd /Users/oneone/Desktop/BNPLGuard
.venv/bin/python -m streamlit run app.py
```

Open the actual printed local URL, normally http://127.0.0.1:8501. Stop that running terminal with Ctrl+C. Do not start a second service on an occupied port or reuse an old PID. PyCharm interpreter: /Users/oneone/Desktop/BNPLGuard/.venv/bin/python; module streamlit; parameters run app.py; working directory the desktop root.

Next: stage-nine real-user feedback, with consent and an explicit protocol, followed by course report/video review and AI-use disclosure. No feedback or student review is invented by this deployment.


## Post-release repository expansion (5 November 2026)

At the user's request the private source repository now includes the reviewed research/team-handoff set, beyond the unchanged99-file inference packaging contract. See deployment/repository_files.json and docs/repository_contents.md. Added study evidence is aggregate only; the received participant workbook remains private.154local regression tests passed in6.27s, the data gate passed and192protected hashes remain unchanged. App source, model, encoded SHAP background, schema, lock and simulator arithmetic are unchanged. Existing Git history/visibility are preserved. This source publication is not a new manual deployment or new anonymous online acceptance; main may refresh automatically through the existing Community Cloud integration. The prior accepted deployed revision is771aadd; use Git history for the newer research handoff revision.


## Stress and instalment release (5 November 2026)

Release marker: `stress-installments-20261105`. Updated Stress input order, savings separation, five visible scenario results and optional monthly instalment estimation. User retest forms are prepared; actual participant retest remains pending. See docs/installment_plan.md, docs/stress_feedback_changes.md and user_testing/retest_v1/. Online acceptance and actual commit must be checked separately; do not infer them from this preparation note.


## Stress and calculator publication update — 5 November 2026

Repository main contains the updated interface and monthly instalment calculator at commit `a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67`, release marker `stress-installments-20261105`. The source was pushed successfully to the existing private repository. At the last anonymous check the public application still displayed the older version and did not show the new marker; Cloud rollout and the new-version online acceptance remain unconfirmed. Do not describe this revision as publicly accepted until the marker and requested interactions are checked. Real participant retesting remains outstanding. No participant responses were fabricated. See user_testing/retest_v1/ for blank materials and docs/installment_plan.md for the current calculation.


## Public acceptance completed — 2026-11-05T23:39:09+11:00

The prior Cloud pending note is superseded. After authorized reboot, an anonymous in-app browser displayed release marker `stress-installments-20261105` from app source commit `a77bc23b6fdb5b54645c5c4d23d7b4aaac6ffb67`. Screen fictional example returned83.85%, eight-feature SHAP and template text. Stress standard buffers900/700/0/-200/1100 AUD;600/0/3 previewed and applied200;100/0/3 displayed33.33/33.34 and applied33.34, yielding866.66 added-plan buffer. Editing invalidated prior results, switching restored manual200, reset cleared fields. Explain global plot and Model saved metrics AP0.7634/AUC0.8432/Brier0.1573 loaded. A390x844 viewport displayed the five standard scenario cards and the100/3 preview, visually inspected; this is emulation, not a physical iPhone or independent user test. Desktop was checked with the normal in-app-browser viewport. Local full regression170 passed; relevant tests32 passed after release marker. Original model, simulator and prior responses remain unchanged. Actual participant retest remains pending. Public app: https://bnplguard-yixuan502.streamlit.app/.
