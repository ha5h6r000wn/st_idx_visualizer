# dev-workflow Specification (Delta)

## ADDED Requirements

### Requirement: Deterministic onboarding for CSV-only runtime
The repository SHALL provide a `README.md` that enables a new contributor to install dependencies and run the Streamlit app using only local CSV snapshots.

#### Scenario: Clone → install → run in minutes
- **WHEN** a contributor clones the repository on a machine with Python `3.12.12`
- **AND** follows the README quickstart using `uv`
- **THEN** `streamlit run app.py` starts successfully using CSV files under `data/csv/` (no database required)
- **AND** `python scripts/run_quick_checks.py` completes successfully.

### Requirement: Runtime/dev dependency separation
The project SHALL keep Streamlit runtime dependencies minimal and SHALL NOT require dev tooling to run the app.

#### Scenario: Runtime install is lean
- **WHEN** a contributor installs runtime dependencies only
- **THEN** dev tools (e.g., `ruff`, `pytest`, `jupyter`) are not installed as part of the runtime dependency set.

### Requirement: Mirror-agnostic dependency lock files
The repository SHALL track dependency exports in requirements format (`requirements.txt` and `requirements-dev.txt`) and MAY keep Poetry configuration temporarily as a fallback for Streamlit Cloud.

#### Scenario: Different indexes do not cause git churn
- **WHEN** two contributors install from different indexes/mirrors
- **THEN** they do not generate git diffs in tracked lock files during normal install flows
- **AND** maintainers update tracked lock files deliberately as an explicit change.

### Requirement: Minimal CI safety net
The repository SHALL provide a GitLab CI pipeline that runs lint and fast tests on merge requests.

#### Scenario: MR runs lint + fast tests
- **WHEN** a merge request is opened
- **THEN** CI runs `ruff check .`
- **AND** runs `python scripts/run_quick_checks.py`
- **AND** uses Python `3.12.12` to match `requires-python`.

### Requirement: Repository hygiene for pre-release
The repository SHALL remove misleading or unused artifacts that imply unsupported workflows.

#### Scenario: No unused devcontainer
- **WHEN** a contributor looks for supported environments
- **THEN** the repository does not include an unused `.devcontainer/` configuration that is not maintained.
