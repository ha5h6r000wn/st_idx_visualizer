## ADDED Requirements

### Requirement: Financial factors stock-pool dataset via CSV DataSource
The system SHALL expose the `financial_factors_stocks.csv` dataset via the CSV-backed `DataSource`, with a declared schema (required columns and dtypes) and deterministic date ordering.

#### Scenario: Fetching stock-pool data for visualization
- **WHEN** the visualization layer fetches financial-factors stock-pool data
- **THEN** the returned DataFrame includes the required columns (including `交易日期` and the three strategy signal columns), uses the declared dtypes, and is ordered by `交易日期` descending.

#### Scenario: Tolerating extra columns in CSV snapshots
- **WHEN** the CSV contains extra columns beyond the declared schema
- **THEN** the loader keeps them on the returned DataFrame (unless explicitly filtered by consumers), preserving forward compatibility.

