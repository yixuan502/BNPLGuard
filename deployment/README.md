# Deployment contract

The reviewed release file list is runtime_files.json. Build a clean tree with `python -m src.deployment build --output deployment/clean_tree_v1`, then check that tree with its locked environment. Community Cloud uses uv.lock before requirements.txt; original requirements files are preserved model-environment evidence, while the effective deployment Python is 3.13. No secrets are required.

The release includes the frozen LR, exact raw-input mapping, fixed SHAP encoded background/config and locked ID membership reference; only aggregate formal evaluation evidence is shipped. Raw datasets, row-level predictions/bootstrap draws, course PDFs, Notebook code, old model runs and local environments are excluded. Original research checks remain local or require separate research data; the portable smoke/deployment tests work without raw CSVs. Public application sharing is distinct from private GitHub source access.
