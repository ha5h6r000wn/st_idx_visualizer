## Context
`financial_factors_backtest_nav.csv` provides daily NAV series for three strategy stock pools and their benchmarks. The UI already offers a fixed-period selector and a combined “NAV lines + excess bars” chart per tab.

This change adds a standard performance table for the selected window and aligns the excess definition to multiplicative relative performance.

## Goals / Non-Goals
- Goals:
  - Provide a single, comparable performance table per tab for the selected window.
  - Use standard definitions for return, annualized return, max drawdown, and Sharpe.
  - Use ratio-based excess so that “excess” is comparable across long horizons.
- Non-Goals:
  - Introducing additional datasets (e.g., risk-free term structure).
  - Replacing the existing period selector logic or adding a full date slider.

## Decisions

### Decision: Use ratio-based excess return (relative NAV)
Define excess as the relative NAV of strategy vs benchmark:
- Window re-base:
  - `strategy_norm[t] = strategy_nav[t] / strategy_nav[t0]`
  - `bench_norm[t] = bench_nav[t] / bench_nav[t0]`
- Excess (relative) NAV:
  - `excess_nav[t] = strategy_norm[t] / bench_norm[t]` (starts at 1)
- Excess return for display:
  - `超额收益[t] = excess_nav[t] - 1`

This replaces the additive definition `strategy_ret - bench_ret`.

### Decision: Compute Sharpe from NAV-derived returns with configurable rf
For any (re-based) NAV series `nav_norm` in the selected window:
- Daily returns:
  - `r[t] = nav_norm[t] / nav_norm[t-1] - 1`
- Annual risk-free rate parameter:
  - `rf_annual` default `0.013`
  - Convert to per-trading-day return:
    - `rf_daily = (1 + rf_annual) ** (1 / TRADING_DAYS) - 1`
- Sharpe:
  - `excess_r = r - rf_daily`
  - `sharpe = mean(excess_r) / std(excess_r) * sqrt(TRADING_DAYS)`

Standard deviation is computed on returns (not NAV levels). When the return series is too short or has zero variance, Sharpe is `NaN`.

### Decision: Annualization and drawdown
- Period return:
  - `period_ret = nav_norm[-1] - 1`
- Annualized return:
  - Use the number of daily return observations `n = len(r)`:
  - `annual_ret = (1 + period_ret) ** (TRADING_DAYS / n) - 1` (when `n > 0`)
- Max drawdown:
  - `dd[t] = nav_norm[t] / max(nav_norm[:t]) - 1`
  - `max_dd = min(dd)`

`TRADING_DAYS` should reuse the project’s existing convention (`config.TRADE_DT_COUNT['一年']`, currently 242).

## UI Placement
Per tab, keep the current order:
1) Stock pool table
2) Backtest NAV chart (same period selector)
3) Performance table (“区间绩效”)

Add a small risk-free rate input (annualized) near the period selector so users can adjust Sharpe assumptions. Default value is 1.3%.

## Risks / Trade-offs
- User-visible semantics change for the excess bars (additive → multiplicative).
  - Mitigation: update labels/documentation and keep the bar axis in percent (`超额收益`).
- Metrics can be unstable for very short windows (e.g., too few points).
  - Mitigation: return `NaN` and display as blank/`-` rather than raising.

