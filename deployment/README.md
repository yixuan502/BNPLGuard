# Application package

`runtime_files.json` specifies the raw-data-free application package. `repository_files.json` specifies the source, tests, technical methods and aggregate evidence included in the submission. Private user records, team instructions, development archives, caches and local environments are excluded.

Build a new package with `python -m src.deployment build --output /path/to/new-runtime-package`. Verify it with `python deployment/smoke.py` in the locked Python 3.13 environment. Community Cloud uses `uv.lock`; no API key is required. See [deployment](../docs/deployment.md) and [data sources](../docs/data_sources.md).
