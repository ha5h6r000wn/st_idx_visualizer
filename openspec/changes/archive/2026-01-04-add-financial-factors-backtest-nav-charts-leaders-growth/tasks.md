## 1. Implementation
- [x] Add a per-strategy chart config (strategy label, NAV column, benchmark column, title, widget key prefix).
- [x] Generalize the existing backtest NAV chart renderer to render a chart for a given strategy config.
- [x] Render the new charts under `财务选股 -> 细分龙头` and `财务选股 -> 景气成长` below the stock pool table.
- [x] Add column presence checks; warn and skip when any required column is missing.
- [x] Keep period options/default consistent with the Dividend Neutral chart; ensure widget keys are unique across tabs.

## 2. Validation
- [x] Run `python -m ruff check visualization/financial_factors_stocks.py`.
- [x] Run `python -m pytest -q`.
- [ ] Run `streamlit run app.py` and verify the two new charts render and update with the period selector.
