## 1. Implementation
- [x] 1.1 Add a pure NAV-metrics calculator (period return, annualized return, max drawdown, Sharpe)
- [x] 1.2 Add an annual risk-free rate parameter (default 1.3%) used by Sharpe
- [x] 1.3 Update excess bars to ratio-based excess return (`strategy_norm / bench_norm - 1`)
- [x] 1.4 Render a per-tab performance comparison table linked to the selected period
- [x] 1.5 Add unit tests for the metrics calculator and ratio-based excess logic
- [x] 1.6 Run `ruff` (touched files) and `pytest`
- [ ] 1.7 Streamlit smoke check on `财务选股` tabs (Streamlit launch is blocked by sandbox permissions in this environment)
