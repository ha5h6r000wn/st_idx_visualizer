## Implementation Tasks (Phased)

### Phase 0 (P0): Unblock onboarding
- [x] Add `README.md` that includes: Python `3.12.12`, `uv` setup, `streamlit run app.py`, CSV contract, and `python scripts/run_quick_checks.py`.
- [x] Fix `pyproject.toml` basics:
  - [x] Replace placeholder `description`.
  - [x] Remove stdlib entries mistakenly listed as dependencies (`logging`, `pathlib`).
  - [x] Move dev-only tooling (`ruff`, `pytest`, `jupyter`) into a dev dependency group.
  - [x] Remove misleading `[tool.poetry]` config unless Poetry is explicitly supported.
- [x] Remove unused `.devcontainer/`.
- [x] Deprecate `csv_update.md` by moving it to `docs/archived/csv_update.md` after extracting any still-relevant “CSV contract” notes into `README.md`.

### Phase 1 (P0/P1): Replace `uv.lock` with requirements lock file(s)
- [x] Decide lock hash policy (A: with hashes).
- [x] Add tracked export files:
  - [x] `requirements.txt` (runtime; used by Streamlit Cloud)
  - [x] `requirements-dev.txt` (runtime + dev)
- [x] Document install flow:
  - [x] Runtime: `uv pip sync requirements.txt`
  - [x] Dev: `uv pip sync requirements-dev.txt`

### Phase 3 (P2): Isolate or remove legacy DB/ETL artifacts
- [x] Remove DB dependencies from runtime installs (`sqlalchemy`, `psycopg2-binary`).
- [x] Delete unused DB/ETL-only modules:
  - [x] `data_preparation/data_access.py`
  - [x] `models.py`
- [x] Defer `sql_template/*` removal to Phase 4 (currently referenced by the runtime).
- [x] Remove vendored third-party directories if they are unused by the runtime:
  - [x] `py_lets_be_rational/` (not tracked in git)
  - [x] `py_vollib/` (not tracked in git)

### Validation
- [x] `python scripts/run_quick_checks.py`
- [x] `streamlit run app.py` (manual smoke: load each tab; confirm CSV loads + charts render)
