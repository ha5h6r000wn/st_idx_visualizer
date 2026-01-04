## ADDED Requirements

### Requirement: Dividend-neutral backtest NAV chart with cumulative excess
The system SHALL render a combined chart under `财务选股 -> 中性股息` (below the stock pool table) showing two NAV lines and a cumulative-excess bar series sourced from `financial_factors_backtest_nav.csv`.

#### Scenario: Rendering the chart in the Dividend Neutral tab
- **WHEN** the user opens the `财务选股` page and selects the `中性股息` tab
- **THEN** the UI renders the stock pool table and then renders the backtest NAV chart below it (or warns when the dataset is unavailable).

#### Scenario: Chart encodings and legend titles
- **WHEN** the chart is rendered
- **THEN** it shows:
  - two lines labeled under legend title `投资标的` for `中性股息` and `中证红利全收益` showing cumulative returns (`净值-1` after per-window rebase),
  - and bars labeled under legend title `累计超额` where bar height is `超额 = 中性股息累计收益 - 中证红利全收益累计收益`.

#### Scenario: Re-base NAV series per selected window
- **WHEN** the user changes the selected date window
- **THEN** both NAV series are independently re-based to `1` at the window start before computing `超额` and rendering the chart.

#### Scenario: Excess color state is based on day-over-day change
- **WHEN** the chart computes the cumulative excess color state
- **THEN** each date is labeled `上涨` if `超额[t] >= 超额[t-1]`, otherwise `回撤`, and the bar colors visually distinguish the two states (lighter for `上涨`, darker for `回撤`).

#### Scenario: Default date window starts at 20180430
- **WHEN** the user first sees the chart
- **THEN** the default selected date window begins at `20180430` (or the first available date on/after it) and ends at the latest available date, and the user can adjust the window via a slider.
