## MODIFIED Requirements

### Requirement: Dividend-neutral backtest NAV chart with cumulative excess
The system SHALL render a combined chart under `财务选股 -> 中性股息` (below the stock pool table) showing two cumulative-return lines and a cumulative-excess bar series sourced from `financial_factors_backtest_nav.csv`.

#### Scenario: Fixed period selection
- **WHEN** the user interacts with the backtest chart date control
- **THEN** the system provides a fixed-period dropdown with options: `2025年`, `近一年`, `近半年`, `2018年5月以来`, and filters the chart to the corresponding window.

#### Scenario: Default period
- **WHEN** the user first sees the chart
- **THEN** the default selected period is `2018年5月以来`.

