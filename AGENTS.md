# BNPLGuard project instructions

The active project root is `/Users/oneone/Desktop/BNPLGuard`. Run project commands with this directory as the working directory. Do not modify the former ChatGPT project copy.

Read `docs/project_spec.md`, `docs/progress.md`, and the relevant code before continuing. Preserve existing results, raw data, and user changes. Everything under `sources/` remains read-only reference material; do not edit synced source files.

All project-authored files must be written in English, including README, specifications, progress records, future deliverables, comments, generated documentation, and application text. Keep raw datasets and third-party source documents unchanged. Historical backups are evidence, not active instructions.

Use `.venv/bin/python`. Run `.venv/bin/python -m src.data_audit` and `.venv/bin/python -m pytest -q` for local checks. Completed training runs must not be overwritten; use a new `--output-dir` only when a new run is necessary.

The CFPB test IDs are locked. Do not evaluate the test set or use it for feature, model, threshold, or calibration selection before the experiment is frozen. Kaggle data must remain separate from CFPB. Read the current progress record for the next authorized stage; migration and translation do not authorize additional modeling.
