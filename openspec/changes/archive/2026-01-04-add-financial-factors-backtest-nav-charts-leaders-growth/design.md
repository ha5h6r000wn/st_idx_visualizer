# Design: Backtest NAV charts for Segment Leaders and Cyclical Growth

## Data model
Source dataset: `data/csv/financial_factors_backtest_nav.csv`

Columns used:
- `交易日期` (string `%Y%m%d`)
- Strategy NAV:
  - `细分龙头股票池` for `细分龙头`
  - `景气成长股票池` for `景气成长`
- Benchmark NAV:
  - `沪深300` for both charts

Derived per selected period:
- Rename the strategy column to the display label (`细分龙头` / `景气成长`) for line legend readability.
- Re-base both NAV series to `1` at the window start and convert to cumulative returns (`nav / nav0 - 1`).
- Compute cumulative excess: `超额 = 策略累计收益 - 沪深300累计收益`.
- Assign excess state: `累计超额` is `正超额` if `超额 >= 0`, else `负超额`.

## Chart composition
Reuse the existing Altair “bar + multi-line with independent color scales” helpers.

- **Bars**
  - X: `交易日期`
  - Y: `超额`
  - Color/legend: `累计超额` (`正超额` vs `负超额`)

- **Lines**
  - X: `交易日期`
  - Y: `累计收益`
  - Series/legend: `投资标的` showing the strategy label and `沪深300`

## UI placement and controls
- Render the chart below the stock pool table in each tab.
- Provide a fixed-period dropdown with the same options and default as the Dividend Neutral chart.
- Use unique Streamlit widget keys per tab to avoid collisions.

## Compatibility
- If the dataset is missing or required columns are absent, the UI warns and skips rendering (no crashes).

