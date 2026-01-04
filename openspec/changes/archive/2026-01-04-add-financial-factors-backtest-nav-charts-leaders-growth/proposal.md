# Change: Add backtest NAV charts for Segment Leaders and Cyclical Growth

## Why
`financial_factors_backtest_nav.csv` now includes NAV series for the Segment Leaders (细分龙头) and Cyclical Growth (景气成长) stock pools plus the CSI 300 benchmark. Users need the same visual NAV + cumulative excess view already available for Dividend Neutral (中性股息), directly in the corresponding tabs.

## What Changes
- Add a combined “cumulative return lines + cumulative excess bars” chart under:
  - `财务选股 -> 细分龙头` using `细分龙头股票池` vs `沪深300`
  - `财务选股 -> 景气成长` using `景气成长股票池` vs `沪深300`
- Reuse the existing Dividend Neutral chart behavior:
  - fixed-period selector (`2025年`, `近一年`, `近半年`, `2018年5月以来`) with default `2025年`
  - per-window NAV re-base to `1` and display `净值-1` as cumulative return
  - compute cumulative excess (`超额`) and color bars by sign (`正超额`/`负超额`)
- Gracefully handle missing columns (warn and skip chart) to avoid breaking older CSV snapshots.

## Impact
- Affected specs: `visualization`
- Affected code (expected): `visualization/financial_factors_stocks.py`
- Backwards compatibility: additive UI change; existing charts and tables remain unchanged.

