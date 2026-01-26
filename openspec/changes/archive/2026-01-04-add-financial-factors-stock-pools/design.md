## Design Overview

This change adds a new "financial factors stock pool" dataset and renders three strategy-specific pools in the Streamlit UI. The design goal is to keep the implementation boring: one dataset schema, one shared filtering/rendering path, and three small configurations.

## Data Model

- Source: `data/csv/financial_factors_stocks.csv`
- Primary slice key: `交易日期`
- Strategy membership signals:
  - `中性股息策略` (0/1)
  - `细分龙头策略` (0/1)
  - `景气成长策略` (0/1)

## UI Behavior

- Location: `visualization/financial_factors_stocks.py` under the existing `财务选股` header and three tabs.
- Each tab contains its own trade-date `selectbox`:
  - options come only from the CSV (`交易日期` unique values),
  - sorted descending (newest → oldest),
  - selecting a date only affects the current tab.
- The stock pool table shows rows where:
  - `交易日期 == selected_date` and the current strategy signal column equals `1`.

## Configuration Surface

- A per-strategy list of display columns is stored in code configuration (persisted, not per-session).
- Default configuration enumerates all CSV columns so a user can delete unwanted fields per strategy.
- Rendering is resilient:
  - if no rows are selected, display an explicit "empty pool" message;
  - if configured columns are missing from the CSV, ignore them with a warning rather than raising.

## Compatibility

- The Streamlit entry point and existing tabs remain unchanged.
- Existing CSV-only data access patterns are reused; no new data sources are introduced.

