# Design: Financial-factors backtest NAV chart

## Data model
Source: `data/csv/financial_factors_backtest_nav.csv`

Required columns:
- `交易日期` (string, `%Y%m%d`)
- `中性股息股票池` (float, NAV)
- `中证红利全收益` (float, NAV)

Derived columns (in the visualization prep step):
- `中性股息` = `中性股息股票池` (rename for legend display)
- Per-selected-window normalization:
  - `中性股息` and `中证红利全收益` are each re-based to 1 at the start of the selected window.
  - `中性股息_norm[t] = 中性股息[t] / 中性股息[t0]`
  - `中证红利全收益_norm[t] = 中证红利全收益[t] / 中证红利全收益[t0]`
- Cumulative return display:
  - `中性股息_ret[t] = 中性股息_norm[t] - 1`
  - `中证红利全收益_ret[t] = 中证红利全收益_norm[t] - 1`
- `超额` = `中性股息_ret - 中证红利全收益_ret`
- `累计超额` (categorical): `上涨` if `超额[t] >= 超额[t-1]`, else `回撤` (first row defaults to `上涨`)

## Chart composition
Reuse the existing Altair “bar+line with independent color scales” helper used by style charts.

- **Bars**
  - X: `交易日期`
  - Y: `超额`
  - Color/legend: `累计超额` with domain order `回撤 -> 上涨` so `上涨` maps to the lighter color.

- **Lines**
  - X: `交易日期`
  - Y: `累计收益`
  - Series/legend: `投资标的` showing `中性股息` and `中证红利全收益`.

## Date window default
Provide a date-range slider and filter the selectable dates to `>= 20180430`. If the dataset does not contain `20180430`, the default start becomes the first available date after it.

## Backwards compatibility
All changes are additive:
- Existing CSV datasets, pages, and chart helpers remain intact.
- When the CSV is missing, the UI warns and skips rendering (no crashes).
