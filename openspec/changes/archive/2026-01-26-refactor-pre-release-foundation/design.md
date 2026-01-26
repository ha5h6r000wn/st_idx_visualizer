# Design Notes: Pre-release foundation refactor

## Data structures and invariants (what matters)
- Runtime input is local CSV snapshots under `data/csv/*.csv`.
- Streamlit runtime must remain CSV-only: no database sessions, no Wind/remote calls in automated checks.
- `requires-python` stays pinned to `==3.12.12` (patch-level pin is intentional).

## Locking strategy (why `requirements*.lock.txt`)
`uv.lock` is expected to churn across environments when different package indexes/mirrors are used. That churn is noise and creates merge conflicts without improving runtime behavior.

Instead:
- Treat `uv.lock` as local/ephemeral.
- Track exports as:
  - `requirements.txt` (runtime-only; Streamlit Cloud-friendly)
  - `requirements-dev.txt` (runtime + dev tooling; contributors)

### Hash policy (open decision)
We must pick one:
- **A: With hashes** (more reproducible; preferred)
  - Works if mirrors serve identical distributions (hashes match).
- **B: Without hashes** (more tolerant)
  - Accepts weaker integrity guarantees but avoids mirror hash mismatches.

## Backward-compatibility guardrail
"Never break userspace": changes MUST NOT alter the Streamlit runtime behavior. These refactors are limited to docs, packaging, repo hygiene, and test scaffolding.
