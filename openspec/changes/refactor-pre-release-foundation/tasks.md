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
- [x] Decide lock hash policy:
  - [x] A: With hashes (preferred; most reproducible)
  - [ ] B: Without hashes (more tolerant across mirrors)
- [x] Add tracked export files:
  - [x] `requirements.txt` (runtime; used by Streamlit Cloud)
  - [x] `requirements-dev.txt` (runtime + dev)
- [x] Document install flow:
  - [x] Runtime: `uv pip sync requirements.txt`
  - [x] Dev: `uv pip sync requirements-dev.txt`

### Phase 3 (P2): Isolate or remove legacy DB/ETL artifacts
- [ ] Mark legacy DB/ETL modules as non-runtime in docs.
- [ ] Move DB dependencies behind an optional group/extra so CSV-only runtime installs do not pull DB libraries.
- [ ] If unused, migrate or delete ETL-only modules and SQL templates:
  - [ ] `data_preparation/data_access.py`
  - [ ] `models.py`
  - [ ] `sql_template/*`
- [ ] Remove vendored third-party directories if they are unused by the runtime:
  - [ ] `py_lets_be_rational/`
  - [ ] `py_vollib/`

### Validation
- [x] `python scripts/run_quick_checks.py`
- [ ] `streamlit run app.py` (manual smoke: load each tab; confirm CSV loads + charts render)
