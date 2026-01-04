## ADDED Requirements

### Requirement: Backtest NAV charts for Segment Leaders and Cyclical Growth
The system SHALL render combined backtest NAV charts under `财务选股 -> 细分龙头` and `财务选股 -> 景气成长` (below the stock pool table) showing two cumulative-return lines and a cumulative-excess bar series sourced from `financial_factors_backtest_nav.csv`.

#### Scenario: Rendering charts in the two tabs
- **WHEN** the user opens the `财务选股` page and selects the `细分龙头` or `景气成长` tab
- **THEN** the UI renders the stock pool table and then renders the corresponding backtest chart below it (or warns when the dataset/columns are unavailable).

#### Scenario: Chart encodings and legend titles
- **WHEN** the `细分龙头` chart is rendered
- **THEN** it shows:
  - two lines labeled under legend title `投资标的` for `细分龙头` and `沪深300` showing cumulative returns (`净值-1` after per-window re-base),
  - and bars labeled under legend title `累计超额` where bar height is `超额 = 细分龙头累计收益 - 沪深300累计收益`.

- **WHEN** the `景气成长` chart is rendered
- **THEN** it shows:
  - two lines labeled under legend title `投资标的` for `景气成长` and `沪深300` showing cumulative returns (`净值-1` after per-window re-base),
  - and bars labeled under legend title `累计超额` where bar height is `超额 = 景气成长累计收益 - 沪深300累计收益`.

#### Scenario: Fixed period selection
- **WHEN** the user interacts with the backtest chart date control
- **THEN** the system provides a fixed-period dropdown with options: `2025年`, `近一年`, `近半年`, `2018年5月以来`, and filters the chart to the corresponding window.

#### Scenario: Default period
- **WHEN** the user first sees either chart
- **THEN** the default selected period is `2025年`.

#### Scenario: Re-base NAV series per selected window
- **WHEN** the user changes the selected period
- **THEN** both NAV series are independently re-based to `1` at the window start before computing cumulative returns, `超额`, and rendering the chart.

#### Scenario: Excess state is based on sign
- **WHEN** the chart assigns the cumulative excess bar signal
- **THEN** it labels each date as `正超额` when `超额 >= 0`, otherwise `负超额`, and the bar colors visually distinguish the two states.

#### Scenario: Missing columns do not crash the UI
- **WHEN** the dataset is present but one or more required columns (`交易日期`, strategy NAV column, `沪深300`) are missing
- **THEN** the UI renders a warning and skips the chart instead of raising.

