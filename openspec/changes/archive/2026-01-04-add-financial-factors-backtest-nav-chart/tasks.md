## 1. Implementation
- [x] Register `FINANCIAL_FACTORS_BACKTEST_NAV` in `config.CSV_FILE_MAPPING` and `config.CSV_DTYPE_MAPPING`.
- [x] Add a dataset schema entry in `data_preparation/data_fetcher.py` and ensure `fetch_data_from_local` returns normalized, date-sorted data.
- [x] Implement a pure prep step to compute:
  - NAV series (`中性股息`, `中证红利全收益`)
  - cumulative excess (`超额`)
  - excess state (`累计超额` = `上涨/回撤`)
- [x] Re-base both NAV series to `1` at the selected window start whenever the date range changes.
- [x] Display cumulative returns (`净值-1`) for both series and use percent axis formatting.
- [x] Render the bar+multi-line chart under `财务选股 -> 中性股息` below the stock pool view, defaulting to dates >= `20180430`.
- [x] Update `csv_update.md` to include `financial_factors_backtest_nav.csv` in app-facing CSV expectations.

## 2. Validation
- [x] Add a schema test for `FINANCIAL_FACTORS_BACKTEST_NAV` similar to existing dataset tests.
- [x] Run `python -m pytest -q`.
- [x] Run `python -m ruff check` for touched files (full-repo ruff currently fails due to an unrelated pre-existing issue in `models.py`).
