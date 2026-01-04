## ADDED Requirements

### Requirement: Financial factors backtest NAV dataset via CSV DataSource
The system SHALL expose the `financial_factors_backtest_nav.csv` dataset via the CSV-backed `DataSource`, with a declared schema (required columns and dtypes) and deterministic date ordering.

#### Scenario: Fetching backtest NAV data for visualization
- **WHEN** the visualization layer fetches `FINANCIAL_FACTORS_BACKTEST_NAV` from the CSV data source
- **THEN** the returned DataFrame includes the required columns (`交易日期`, `中性股息股票池`, `中证红利全收益`), uses the declared dtypes, and is ordered by `交易日期` descending.

#### Scenario: Missing CSV does not break the UI
- **WHEN** the CSV snapshot `financial_factors_backtest_nav.csv` is missing
- **THEN** the data source returns an empty DataFrame and the visualization layer renders a warning instead of raising.

