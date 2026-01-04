## 1. Implementation
- [x] 1.1 Register `financial_factors_stocks.csv` in the CSV data layer (file mapping, dtypes, schema, and a fetch method).
- [x] 1.2 Add a persistent per-strategy display-column configuration listing all CSV columns by default.
- [x] 1.3 Implement per-tab trade-date selectboxes (dates from CSV only; descending) and filtered stock-pool rendering.
- [x] 1.4 Make the table rendering resilient (empty pools show a clear message; missing configured columns are ignored with a warning).
- [x] 1.5 Add minimal, Streamlit-free tests for schema invariants and basic filtering behavior.

## 2. Validation
- [x] 2.1 Run `pytest -q` (focus on schema and prep tests).
- [x] 2.2 Run `streamlit run app.py` and smoke-check the "财务选股" tab across all three strategies.
