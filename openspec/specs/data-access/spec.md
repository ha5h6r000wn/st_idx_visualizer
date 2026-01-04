# data-access Specification

## Purpose
TBD - created by archiving change refactor-data-layer. Update Purpose after archive.
## Requirements
### Requirement: CSV-only data source abstraction
The system SHALL expose a single CSV-backed `DataSource` used by the Streamlit app, providing dataset-specific fetch methods with normalized schemas and no branching on alternative sources in visualization modules.

#### Scenario: Constructing the app data source
- **WHEN** the Streamlit visualization modules fetch data
- **THEN** they construct or receive only the CSV implementation, and do not create database sessions or branch on a database-backed path.

#### Scenario: Updating dataset filters and schemas
- **WHEN** dataset filters (e.g., bond yield curve names/terms) or canonical schemas are updated in metadata
- **THEN** the change is applied via the CSV `DataSource` implementation and a single canonical schema definition per dataset, without introducing duplicate schema definitions in multiple modules.

### Requirement: Normalized dataset schema
The system SHALL normalize each dataset into a canonical schema immediately after loading (e.g., trade_date, code, name/value columns) and provide optional aliases for existing Chinese labels used by charts, defined in a single source of truth per dataset.

#### Scenario: Bond yield normalization
- **WHEN** bond yield data is loaded from CSV
- **THEN** the returned DataFrame includes canonical columns (`trade_date`, `curve_name`, `curve_term`, `ytm`) and original Chinese columns, as defined by one shared schema object.

#### Scenario: Index price normalization
- **WHEN** index price data is loaded from CSV with Chinese physical headers (e.g., `交易日期`, `证券代码`, `证券简称`, `收盘价`)
- **THEN** the returned DataFrame includes:
  - the physical Chinese columns (and tolerates extra columns like `id`, `更新时间`),
  - legacy/raw Wind columns (`TRADE_DT`, `S_INFO_WINDCODE`, `S_INFO_NAME`, `S_DQ_CLOSE`) for existing consumers,
  - canonical English aliases (`trade_date`, `wind_code`, `wind_name`, `close`),
  - and consistent dtypes based on the same schema definition.

### Requirement: Removal of unused database path
The system SHALL remove unused database session code and configuration switches from the app runtime so that only the CSV data path remains active for the Streamlit app, while leaving any ETL-specific database models or helpers clearly isolated if they are still needed.

#### Scenario: Database code paths
- **WHEN** data fetching functions used by the Streamlit app are executed
- **THEN** no database sessions are created, and no configuration flags for database selection remain in the visualization or data-preparation code paths; any remaining database helpers are clearly marked as ETL-only and unused by the UI.

### Requirement: Financial factors stock-pool dataset via CSV DataSource
The system SHALL expose the `financial_factors_stocks.csv` dataset via the CSV-backed `DataSource`, with a declared schema (required columns and dtypes) and deterministic date ordering.

#### Scenario: Fetching stock-pool data for visualization
- **WHEN** the visualization layer fetches financial-factors stock-pool data
- **THEN** the returned DataFrame includes the required columns (including `交易日期` and the three strategy signal columns), uses the declared dtypes, and is ordered by `交易日期` descending.

#### Scenario: Tolerating extra columns in CSV snapshots
- **WHEN** the CSV contains extra columns beyond the declared schema
- **THEN** the loader keeps them on the returned DataFrame (unless explicitly filtered by consumers), preserving forward compatibility.

### Requirement: Financial factors backtest NAV dataset via CSV DataSource
The system SHALL expose the `financial_factors_backtest_nav.csv` dataset via the CSV-backed `DataSource`, with a declared schema (required columns and dtypes) and deterministic date ordering.

#### Scenario: Fetching backtest NAV data for visualization
- **WHEN** the visualization layer fetches `FINANCIAL_FACTORS_BACKTEST_NAV` from the CSV data source
- **THEN** the returned DataFrame includes the required columns (`交易日期`, `中性股息股票池`, `中证红利全收益`), uses the declared dtypes, and is ordered by `交易日期` descending.

#### Scenario: Missing CSV does not break the UI
- **WHEN** the CSV snapshot `financial_factors_backtest_nav.csv` is missing
- **THEN** the data source returns an empty DataFrame and the visualization layer renders a warning instead of raising.

