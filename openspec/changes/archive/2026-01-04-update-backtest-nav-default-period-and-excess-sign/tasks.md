## 1. Implementation
- [x] Change the backtest chart default period to `2025年`.
- [x] Update the excess bar legend labels to `正超额/负超额` and assign them by the sign of `超额` (`>=0` vs `<0`).
- [x] Keep per-window rebase and cumulative-return display unchanged.

## 2. Validation
- [x] Run `python -m pytest -q`.
- [x] Run `python -m ruff check visualization/financial_factors_stocks.py`.
