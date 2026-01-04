## ADDED Requirements

### Requirement: Per-strategy stock pools filtered by trade date
The system SHALL render three independent stock-pool views (中性股息 / 细分龙头 / 景气成长) sourced from `financial_factors_stocks.csv`.

#### Scenario: Selecting a trade date for a single strategy
- **WHEN** the user selects a `交易日期` in one strategy tab
- **THEN** only that tab updates, and the rendered table includes only rows for the selected `交易日期` where the strategy signal equals `1`.

#### Scenario: Date options come from CSV only
- **WHEN** the user opens the trade-date dropdown
- **THEN** the options list contains only dates present in the CSV and is sorted newest-to-oldest.

### Requirement: Persistent, per-strategy display-column configuration
The system SHALL provide a persistent (code-based) configuration that defines the ordered set of columns displayed for each strategy stock pool.

#### Scenario: Customizing displayed fields per strategy
- **WHEN** the configured display columns are edited for a given strategy
- **THEN** the stock-pool table for that strategy displays exactly those columns (in order), independent of the other strategies.

#### Scenario: Missing configured columns do not crash the UI
- **WHEN** the configured display columns include fields not present in the current CSV snapshot
- **THEN** the UI renders without raising and warns that the missing fields were ignored.

