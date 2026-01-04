# visualization Specification

## Purpose
TBD - created by archiving change refactor-data-layer. Update Purpose after archive.
## Requirements
### Requirement: Separated chart data preparation
The system SHALL provide pure data-preparation functions for bar+line-with-signal and style framework charts that produce the frames needed for rendering, independent of Streamlit state and widget interactions.

#### Scenario: Prepare once, render multiple
- **WHEN** chart data is prepared for a slider-selected window or style block (e.g., value vs growth, term spread, ERP, style focus)
- **THEN** the resulting DataFrame can be passed to the rendering helper without recomputing signals or re-parsing slider inputs, and can be reused across multiple charts or contexts.

#### Scenario: Reuse outside Streamlit
- **WHEN** a prep function is invoked from a test or CLI context
- **THEN** it returns the same structure as the Streamlit path, enabling validation without UI dependencies.

### Requirement: Minimal chart configuration surface
The system SHALL reduce chart helpers to accept only the fields actually used for encoding (axis names/types, number formatting, colors, stroke dash, legend placement) and avoid nested Pydantic wrappers or behavior flags when a flat configuration suffices.

#### Scenario: Add new style chart variant
- **WHEN** a new style chart variant (e.g., another macro signal) is added
- **THEN** it can be configured by passing a flat config object that does not embed widget configuration or behavioral flags (such as `isLineDrawn`, `isConvertedToPct`, `isSignalAssigned`), and no nested models are required when a single object suffices.

### Requirement: Remove dead chart code
The repository SHALL not contain large commented-out chart helper implementations or unused visualization code paths.

#### Scenario: Legacy test helper and debug remnants
- **WHEN** the previous `draw_test` helper, duplicate bar+line+signal rendering paths, or large commented blocks are unused
- **THEN** they are removed rather than left as commented blocks, keeping only minimal domain-explanatory comments.

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

