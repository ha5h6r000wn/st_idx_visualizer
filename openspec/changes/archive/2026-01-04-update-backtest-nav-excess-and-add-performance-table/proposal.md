# Change: Update backtest NAV excess and add performance table

## Why
The financial-factors tabs currently show NAV lines and an “excess” bar series, but users still need a compact, period-based performance summary (return, annualized return, max drawdown, Sharpe) for the strategy, benchmark, and excess.

In addition, the current excess definition is additive (`strategy - benchmark`). For long horizons, multiplicative relative performance (`strategy / benchmark`) is a more standard and more comparable definition.

## What Changes
- Add a per-tab performance comparison table under the existing backtest NAV chart, linked to the same fixed-period selector (`2025年`, `近一年`, `近半年`, `2018年5月以来`).
- Compute metrics from NAV-derived daily return series (Sharpe uses the standard deviation of returns, not NAV levels).
- Switch the cumulative excess bars from additive excess to ratio-based excess return:
  - `超额收益 = (1 + 策略累计收益) / (1 + 基准累计收益) - 1` (equivalently `策略_norm / 基准_norm - 1` after per-window re-base).
- Add an annualized risk-free rate parameter for Sharpe (default: 1.3% for 1Y CGB yield).

## Impact
- Affected specs: `visualization`
- Affected code:
  - `visualization/financial_factors_stocks.py` (excess calculation + new table + risk-free parameter UI)
  - (optional) a small shared metrics helper module if it improves testability
- Backwards compatibility:
  - Layout and data requirements remain unchanged.
  - Excess bar semantics will change (values differ) but charts remain available and stable.

