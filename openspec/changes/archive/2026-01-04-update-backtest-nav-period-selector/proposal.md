# Change: Update backtest NAV chart period selector

## Why
The Dividend Neutral backtest chart currently uses a free date-range slider. Users want faster, consistent navigation via fixed, named windows rather than arbitrary date picking.

## What Changes
- Replace the free date-range slider in the `财务选股 -> 中性股息` backtest chart with a fixed-period dropdown selector.
- Supported periods:
  - `2025年`
  - `近一年`
  - `近半年`
  - `2018年5月以来`

## Impact
- Affected specs: `visualization`
- Affected code (expected): `visualization/financial_factors_stocks.py`
- Backwards compatibility: chart encodings remain unchanged; only the date selection control changes.

