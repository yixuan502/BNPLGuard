# Stress feedback revision and local acceptance

Date:5 November2026. Revision:`stress-feedback-v1`, based on local/remote main `d67f0ba9341671fe814f82ad3561845919703023`. Local modifications only; no commit, push, manual deployment, video or course-report writing in this round. Public deployment has not received this revision.

## Feedback-to-change record

| Recorded issue | Implemented change | Acceptance |
|---|---|---|
| Savings confused with income | Five flow labels explicitly monthly; separate Savings balance today section, current-available-balance label and explanation that savings affect coverage, not income/buffer | UI assertions and desktop/narrow Chrome screenshots; savings doubled in test without changing cash buffers |
| Field finding/order difficult | One ordered column: I,E,D,B0,Bnew,S; visible exclusions distinguish living costs, non-BNPL debt, current BNPL and proposed BNPL | Browser bounding-box order checked at1280x900 and390x844; same order at both widths |
| Scenario results required inspection | Five always-expanded cards show title, final monthly buffer, change from Current and explicit Surplus/Shortfall/Break-even text | Standard buffers900/700/0/-200/1100AUD visible together in the document, using normal vertical scrolling; no dropdown required for these results |
| Final amount confused with change | Separate labels and short distinction; submitted shock/new repayment/reduction assumptions beside results | Combined final-200 versus change-1100AUD; selected details retain RTI, coverage and the existing template |

The original result-template producer, financial formulas, model, eight input mappings, SHAP background/method and threshold remain unchanged. Screen input labels/options are unchanged. Kaggle stays appendix-only; LLM stays off. New status words describe the sign of the existing buffer; they are not risk grades. Input callbacks still clear submitted results and explanations immediately; resubmission binds all cards/details to one snapshot.

## Actual checks

- Full regression:155passed in12.07s, including the new order/cards/savings/reset test and existing numerical, zero-denominator, negative-input, invalid-reduction, template-consistency, SHAP and API-off checks.
- CFPB data audit:PASS6394x217,6350eligible,2454positive. No training or new formal evaluation.
- Isolated headless Google Chrome, actual local URL:1280x900 desktop and390x844 narrow viewport. Clicked visible Stress navigation and fictional preset, submitted five scenarios, changed input and verified stale results disappeared, reset and checked empty fields, submitted zeros and checked explained N/A. No horizontal overflow. Saved screenshots visually inspected; ordinary page scrolling is required for long content.
- The first automation attempt targeted the styled native radio input and was intercepted by its visible wrapper; the corrected check clicked the visible Stress label. This was a selector issue, not an application repair or a completed first-pass acceptance.
- Browser checks use emulation, not a physical phone/tablet. Safari/Firefox, screen readers and real participant comprehension were not validated this round. Automated/browser success is not evidence of improved user understanding.
- Preservation hashes and changed source hashes:outputs/app/stress_feedback_v1/acceptance.json. Original participant workbook, earlier answer key/scores, original research artifacts and all captured core files remain unchanged.

## Retest and outstanding publication

Use `user_testing/retest_v1/retest_form.md` (all outcome/metadata cells blank) with `facilitator_notes.md`. Record test date, base commit plus local revision, device/browser, returning/new status, independent attempts, exact prompts and post-prompt answers separately. Store completed records only in ignored user_testing/private/. Earlier missing dates, independent app answers and S1 wording remain missing; this new session cannot reconstruct them.

For a local session, open http://127.0.0.1:8501 on the machine running Streamlit. Use a fresh browser session and manually enter the fictional case; do not load the preset when testing field finding. The facilitator-only guide contains expected results. Participants should attempt tasks before help, then give their own words about any confusion. Returning users have practice exposure; label it. There are no completed retest outcomes yet.

Pending publication: src/app_inputs.py, src/app_ui.py, tests/test_app.py, updated documentation, retest materials and local QA evidence. The repository allowlist is updated locally so new materials are visible for review; the inference manifest is unchanged. A separate authorization is required before pushing this revision. After publication, verify the actual Cloud revision and public interactions before claiming remote availability of the improvements.

Start from the project root with `.venv/bin/python -m streamlit run app.py`; stop that terminal with Ctrl+C. If8501 is occupied, use the already-running checked app; do not start a second server or reuse an old PID. PyCharm uses the project's .venv/bin/python, module streamlit, parameters run app.py, project root as working directory.
