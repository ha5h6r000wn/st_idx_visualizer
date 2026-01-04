## 1. Implementation
- [x] Add a fixed-period selector (dropdown) for the Dividend Neutral backtest chart and remove the free date slider.
- [x] Implement deterministic window mapping for: `2025年`, `近一年`, `近半年`, `2018年5月以来`.
- [x] Keep per-window rebase, cumulative-return display, and excess-bar coloring behavior unchanged.

## 2. Validation
- [x] Run `python -m pytest -q`.
- [x] Run `python -m ruff check visualization/financial_factors_stocks.py`.
