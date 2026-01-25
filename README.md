# st-idx-visualizer

Streamlit dashboard for Chinese equity research. Visualizes strategy index performance vs benchmarks and provides style diagnostics (value/growth, large/small) with macro signals.

## Quickstart

Prereqs:
- Python `3.12.12` (exact; enforced by `pyproject.toml`)
- `uv` (tested with `0.9.16`)

Commands:
```bash
uv venv --python 3.12.12
uv sync
uv run streamlit run app.py
```

## Data (CSV-only runtime)

The app reads local CSV snapshots under `data/csv/`.

Required files and required columns are defined in `config/config.py` (`CSV_FILE_MAPPING` + `CSV_DTYPE_MAPPING`).

At minimum, these CSVs must exist:
- `data/csv/index_prices.csv`
- `data/csv/bond_yields.csv`
- `data/csv/index_valuations.csv`
- `data/csv/economic_data.csv`
- `data/csv/shibor_prices.csv`
- `data/csv/financial_factors_stocks.csv`
- `data/csv/financial_factors_backtest_nav.csv`

CSV headers are part of the contract. Many columns are Chinese labels (e.g. `交易日期`) and are relied upon by the app.

## Quick checks (fast pytest)

```bash
uv sync --group dev
uv run python scripts/run_quick_checks.py
```

These checks are intended to stay CSV-only (no DB/Wind calls).

## Updating CSV snapshots

- Include `data/csv/financial_factors_stocks.csv` and `data/csv/financial_factors_backtest_nav.csv` when updating snapshots for the Streamlit app.
- Keep CSV headers stable (the app relies on exact column names such as `交易日期` and the strategy signal columns).
- If headers or types change, update the corresponding schema/dtype declarations and tests before merging.
