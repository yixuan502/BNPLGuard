# Stage 8 deployment record

Date: 5 November 2026. Status: preparing clean-tree verification and private GitHub publication; no public app URL or online acceptance claimed yet.

Target: yixuan502/BNPLGuard, main, app.py, Python 3.13. Original project had no .git directory or remote. GitHub connector and authenticated CLI identity were verified as yixuan502; both initially reported the target repository absent. The private repository https://github.com/yixuan502/BNPLGuard has now been created under the verified account. Course project pp. 3–4 allow public code or instructor access, so private code is compatible provided instructor access is granted before the deadline. The application itself must be public without login.

The old local service was stopped. It was restarted from the project .venv at the actual terminal URL http://127.0.0.1:8501; / and /_stcore/health returned 200. The old in-app browser session was disconnected; reloading it re-established interaction. A fictional questionnaire produced 83.85% with matching eight-input SHAP/template, and the Stress example completed. This is local verification, not online acceptance.

Cloud packaging uses an explicit file allowlist and uv.lock with Python 3.13, preserving original model-package versions. Fictional presets and source metadata are now standalone runtime configs, avoiding a dependency on local research receipts or unrelated course metadata. Frozen model, label, schema, split, SHAP background and formal evaluation bytes remain unchanged.

Streamlit Community Cloud currently presents a sign-in page whose Continue to sign-in action accepts terms and may require GitHub OAuth. Those account/legal actions must be completed by the user after the release is ready; no password or token is requested in chat. LLM remains disabled; Kaggle remains report-appendix only.


### Isolated release check passed

The new raw-data-free checkout with its own uv-created .venv passed all four areas in 72.488 seconds including first-run dependency/font-cache initialization. Probability 0.8384946129177755, maximum SHAP reconstruction error 6.661338147750939e-16; simulator buffers 900/700/0/-200/1100; saved Model metrics AP 0.7634/AUC 0.8432/Brier 0.1573. No unavailable-evidence warning occurred. The 45-second initial deadline was too short for that cold start; the portable check now allows 120 seconds. This is an isolated AppTest run, not anonymous public acceptance.


## Private GitHub release verified; Cloud login pending

Repository: https://github.com/yixuan502/BNPLGuard (private), branch main, entry app.py, Python 3.13, no secrets. Initial app release commit: ffa92490dcf1c38793afe7d6313ae02beddc63e5. The actual remote repository was cloned afresh, with all 98 reviewed files, no raw data and its own uv-locked .venv. All four AppTest areas passed in 81.745 seconds, including first-run font-cache initialization. Prediction, SHAP, offline-template, five simulator buffers and aggregate Model metrics matched the isolated-tree check. This verifies the published file set and is not cloud/anonymous acceptance. Later documentation/ignore-policy commits do not alter the validated numerical app behavior.

The required local data audit also passed: 6394x217, 6350 eligible, 2454 positives. Original protected files remain unchanged. The local service was restarted again after portable-path changes; its actual terminal URL is http://127.0.0.1:8501. The fictional questionnaire and eight-input SHAP/template were rechecked in the browser after restart. Release exceptions are root-anchored; unrelated nested documentation remains ignored.

The only current external blocker is Community Cloud sign-in/terms and any GitHub OAuth authorization. The user must complete those account actions in the browser, without sending passwords/tokens in chat. Then select repository yixuan502/BNPLGuard, branch main, app.py, Advanced Python 3.13, and no secrets. If private repository authorization is required, grant only the repository access needed. Deploy, inspect real build logs, set application Sharing to public (repository remains private), and verify a fresh browser with no Streamlit login. No actual cloud build, public URL or anonymous four-area check has occurred yet. Do not send a guessed URL to the instructor. Real-user feedback remains a subsequent stage.
