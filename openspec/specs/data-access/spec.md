# data-access Specification

## Purpose
TBD - created by archiving change refactor-data-layer. Update Purpose after archive.
## Requirements
### Requirement: CSV-only data source abstraction
The system SHALL expose a single CSV-backed `DataSource` selected via one construction point, providing dataset-specific fetch methods with normalized schemas and no branching on alternative sources.

#### Scenario: Constructing the data source
- **WHEN** the data source object is constructed
- **THEN** it initializes only the CSV implementation and injects dataset metadata for filters without exposing database toggles.

#### Scenario: Updating dataset filters
- **WHEN** dataset filters (e.g., bond yield curve names/terms) are updated in metadata
- **THEN** the change is applied by the CSV `DataSource` implementation without introducing new `if CURRENT_DATA_SOURCE` branches in consumers.

### Requirement: Normalized dataset schema
The system SHALL normalize each dataset into a canonical schema immediately after loading (e.g., trade_date, code, name/value columns) and provide optional aliases for existing Chinese labels used by charts.

#### Scenario: Bond yield normalization
- **WHEN** bond yield data is loaded from CSV or database
- **THEN** the returned DataFrame includes columns `trade_date`, `curve_name`, `curve_term`, `ytm` with numeric types, while Chinese aliases remain available for charts that still expect them.

#### Scenario: Index price normalization
- **WHEN** index price data is loaded from any source
- **THEN** the returned DataFrame includes columns `trade_date`, `wind_code`, `name`, `close` with consistent dtypes.

### Requirement: Removal of unused database path
The system SHALL remove the unused database session code and configuration switches so that only the CSV data path remains active.

#### Scenario: Database code paths
- **WHEN** data fetching functions are executed
- **THEN** no database sessions are created, and no configuration flags for database selection remain.

