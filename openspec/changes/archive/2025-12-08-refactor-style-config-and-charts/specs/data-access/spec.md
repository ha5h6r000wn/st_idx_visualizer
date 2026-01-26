## MODIFIED Requirements

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
- **WHEN** index price data is loaded from CSV
- **THEN** the returned DataFrame includes canonical columns (`trade_date`, `wind_code`, `wind_name`, `close`) and original Wind columns, with consistent dtypes based on the same schema definition.

### Requirement: Removal of unused database path
The system SHALL remove unused database session code and configuration switches from the app runtime so that only the CSV data path remains active for the Streamlit app, while leaving any ETL-specific database models or helpers clearly isolated if they are still needed.

#### Scenario: Database code paths
- **WHEN** data fetching functions used by the Streamlit app are executed
- **THEN** no database sessions are created, and no configuration flags for database selection remain in the visualization or data-preparation code paths; any remaining database helpers are clearly marked as ETL-only and unused by the UI.
