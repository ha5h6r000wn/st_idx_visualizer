# Change: Refactor pre-release foundation (onboarding, locking, hygiene)

## Why
Onboarding is currently fragile and misleading: `pyproject.toml` references a missing `README.md`, runtime dependencies include stdlib and dev-only tools, and `uv.lock` churn is expected across different package indexes/mirrors.

## What Changes
- Add a deterministic onboarding path (README + quick checks) that matches the actual runtime: Streamlit + local CSV snapshots.
- Restructure dependencies so runtime installs stay minimal; move dev-only tooling into a dev group; gate DB/ETL deps behind an optional group/extra.
- Track exported `requirements.txt` / `requirements-dev.txt` for deterministic installs across environments and Streamlit Cloud; keep Poetry fallback until Streamlit Cloud is confirmed stable on `requirements.txt`.
- Remove or quarantine misleading/noisy repository artifacts (unused devcontainer, archived docs, vendored libraries if unused).

## Impact
- Affected specs: `dev-workflow` (new), `data-access` (documentation alignment only; no behavior change intended)
- Affected code/config (implementation stage):
  - `README.md`, `pyproject.toml`, `.gitignore`
  - `scripts/run_quick_checks.py`
  - potential removal/move: `.devcontainer/`, `csv_update.md`, `py_vollib/`, `py_lets_be_rational/`

## Non-goals
- No chart/data pipeline rewrites.
- No re-architecture of SQL alias/style logic in this pre-release pass.
- No change to `requires-python == 3.12.12`.
