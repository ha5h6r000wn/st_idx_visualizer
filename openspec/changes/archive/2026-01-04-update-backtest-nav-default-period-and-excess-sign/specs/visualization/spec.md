## MODIFIED Requirements

### Requirement: Dividend-neutral backtest NAV chart with cumulative excess
The system SHALL render a combined chart under `财务选股 -> 中性股息` (below the stock pool table) showing two cumulative-return lines and a cumulative-excess bar series sourced from `financial_factors_backtest_nav.csv`.

#### Scenario: Rendering the chart in the Dividend Neutral tab
- **WHEN** the user opens the `财务选股` page and selects the `中性股息` tab
- **THEN** the UI renders the stock pool table and then renders the backtest chart below it (or warns when the dataset is unavailable).

#### Scenario: Chart encodings and legend titles
- **WHEN** the chart is rendered
- **THEN** it shows:
  - two lines labeled under legend title `投资标的` for `中性股息` and `中证红利全收益` showing cumulative returns (`净值-1` after per-window rebase),
  - and bars labeled under legend title `累计超额` where bar height is `超额 = 中性股息累计收益 - 中证红利全收益累计收益`.

#### Scenario: Fixed period selection
- **WHEN** the user interacts with the backtest chart date control
- **THEN** the system provides a fixed-period dropdown with options: `2025年`, `近一年`, `近半年`, `2018年5月以来`, and filters the chart to the corresponding window.

#### Scenario: Default period
- **WHEN** the user first sees the chart
- **THEN** the default selected period is `2025年`.

#### Scenario: Re-base NAV series per selected window
- **WHEN** the user changes the selected period
- **THEN** both NAV series are independently re-based to `1` at the window start before computing cumulative returns, `超额`, and rendering the chart.

#### Scenario: Excess signal is based on sign
- **WHEN** the chart assigns the cumulative excess bar signal
- **THEN** it labels each date as `正超额` when `超额 >= 0`, otherwise `负超额`, and the bar colors visually distinguish the two states (lighter for `正超额`, darker for `负超额`).

