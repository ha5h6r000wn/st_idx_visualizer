# Change: Add financial-factors backtest NAV chart

## Why
The financial-factors page currently shows only the per-date stock pool. Users also need a direct, visual comparison of the Dividend Neutral strategy NAV versus the CSI Dividend Total Return benchmark, including the cumulative excess and whether excess is rising or drawing down.

## What Changes
- Add a new CSV dataset `financial_factors_backtest_nav.csv` to the CSV-backed `DataSource` with a declared schema and dtypes.
- Render a combined chart under `财务选股 -> 中性股息` (below the stock pool table):
  - **Lines (NAV):** `中性股息` and `中证红利全收益` with legend title `投资标的`.
  - **Bars (cumulative excess):** `超额 = 中性股息 - 中证红利全收益`, with legend title `累计超额` and categories `上涨/回撤` based on whether today’s excess is `>=` yesterday’s.
  - Default date window starts at `20180430` (or the first available date on/after it).

## Impact
- Affected specs: `data-access`, `visualization`
- Affected code (expected): `config/config.py`, `data_preparation/data_fetcher.py`, `visualization/financial_factors_stocks.py`, `tests/test_data_fetcher_schema.py`
- Backwards compatibility: additive only; existing pages/datasets remain unchanged.

