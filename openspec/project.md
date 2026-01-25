# Project Context

## Purpose
Interactive Streamlit dashboard for Chinese equity research. Visualizes strategy index performance vs benchmarks and provides style diagnostics (value/growth, large/small) with macro signals to support trading and allocation decisions.

## Tech Stack
- Python 3.12
- Streamlit + Altair for UI and charting
- pandas/NumPy for data prep; pydantic for typed config objects
- CSV-backed mode with data under `data/`
- Tooling: ruff linting; `pyproject.toml` + `uv.lock` for packaging

## Project Conventions

### Code Style
- Python snake_case for functions/vars; constants upper snake case
- Configuration and parameters live in `config/` using pydantic models (`param_cls.py`) and module-level constants (`config.py`, `style_config.py`)
- Chart helpers live in `visualization/data_visualizer.py`; Streamlit pages (`visualization/stg_idx.py`, `visualization/style.py`) stay lean and compose helpers
- Prefer explicit parameter objects over global state; keep functions focused on a single transformation
- Keep numeric formatting consistent via `config.CHART_NUM_FORMAT`; many labels remain in Chinese

### Architecture Patterns
- Entry point `app.py` sets Streamlit layout and tabs
- `data_preparation/` handles CSV IO, reshaping, and signal calculations; `visualization/` renders charts; `config/` holds constants/query params; `utils.py` has shared helpers (env loading, date windows, SQL parsing)
- Data source is CSV-only; consumers call fetch helpers without toggles or database branches
- Data flow: fetch raw data → process to wide/long frames → render via Altair; chart configuration driven by parameter objects for consistent axes/legends

### Testing Strategy
- No automated tests yet
- Validate changes by running `streamlit run app.py` and exercising tabs/sliders to confirm data loads and charts render
- Prefer using CSV fixtures under `data/` for development; avoid live DB/Wind calls unless credentials and access are available

### Git Workflow
- Default branch `main`; develop in short-lived feature branches
- Small, descriptive commits; avoid force-pushing shared branches
- Run lint (`ruff`) and a quick Streamlit smoke test before raising PRs

## Domain Context
- Focused on A-share strategy indices (`STG_IDX_CODES`) vs benchmarks (e.g., CSI 800) with date format `%Y%m%d`
- Style module compares value vs growth and large vs small cap indices, plus macro signals from bond yields, Shibor, and selected EDB indicators
- Slider defaults align with average Chinese trading days; chart titles/axes are primarily Chinese

## Important Constraints
- Default to CSV data under `data/csv`; DB/Wind access requires valid credentials and should not be exercised in automated tests
- Preserve existing chart labels/axis names; layout expects specific Chinese labels and column aliases
- Use shared number formats from `config.CHART_NUM_FORMAT`; many calculations assume wide-form frames ordered per config constants

## External Dependencies
- Wind data schemas via SQL templates in `sql_template/` (requires credentials to query)
- Streamlit runtime and Altair for visualization; pandas/NumPy for analytics; openpyxl for Excel ingestion when needed
