# Change: Update backtest chart default period and excess signal

## Why
Users want the backtest chart to default to the `2025年` window. Also, the excess bar colors should reflect whether cumulative excess is positive or negative, not day-over-day changes.

## What Changes
- Default period for the `财务选股 -> 中性股息` backtest chart becomes `2025年`.
- Bar legend and signal logic changes:
  - `正超额` (light color): `超额 >= 0`
  - `负超额` (dark color): `超额 < 0`

## Impact
- Affected specs: `visualization`
- Affected code (expected): `visualization/financial_factors_stocks.py`
- Backwards compatibility: chart layout remains the same; only defaults and bar signal semantics change.

