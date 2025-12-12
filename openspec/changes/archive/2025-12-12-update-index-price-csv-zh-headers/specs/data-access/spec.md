## MODIFIED Requirements

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

