# Change: Add financial-factors stock pools per strategy

## Why
- The "财务选股" page is currently a stub and does not surface any stock pools to the user.
- Users need to inspect three strategy-specific stock pools independently by trade date, using only dates present in the CSV snapshot.
- The dataset already exists under `data/csv/financial_factors_stocks.csv`; the app should expose it through the same CSV-only data-access path used elsewhere.

## What Changes
- Add a CSV dataset schema for `financial_factors_stocks.csv` and expose it through the existing CSV-backed `DataSource`.
- Implement three strategy tabs (中性股息 / 细分龙头 / 景气成长) that:
  - each contains its own trade-date selectbox (newest-to-oldest, limited to dates present in the CSV),
  - filters the dataset to `交易日期 == selected_date` and `strategy_signal == 1`,
  - renders a stock-pool table using a per-strategy configurable column list.
- Update documentation to describe the new dataset and configuration surface.

## Impact
- Affected specs: data-access, visualization
- Affected code: `data_preparation/data_fetcher.py`, `config/*`, `visualization/financial_factors_stocks.py`, `tests/*`
- No code changes until this proposal is approved.
