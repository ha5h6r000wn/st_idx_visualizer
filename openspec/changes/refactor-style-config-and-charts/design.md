## Design Overview

The design goal is to make the style and strategy-index visualization paths boringly simple: one clear data-prep function per chart type, one simple config object per chart, and a CSV-only data layer. We keep all current behavior while eliminating unnecessary branching and duplicated logic.

### 1. Data-access and schema consolidation

**Current state**

- `data_preparation/data_fetcher.py` implements `CSVDataSource` with:
  - `read_csv_data(table_name: str)` using `config.CSV_DTYPE_MAPPING`,
  - `CANONICAL_COL_MAPPINGS` to add normalized English aliases,
  - `fetch_index_data_from_local` and `fetch_data_from_local` wrappers.
- `data_preparation/data_access.py` and `models.py` implement SQLAlchemy models and session-based fetchers that are not called by the Streamlit app.
- `config.config`, `config.style_config`, `config.param_cls`, and `CANONICAL_COL_MAPPINGS` all carry fragments of schema knowledge.

**Problems**

- Multiple schema definitions risk drift and confusion; it is not obvious which one is canonical.
- `CSVDataSource.fetch_table` has type-mismatched logic when detecting the date column for `A_IDX_PRICE`.
- The presence of unused database session helpers makes the real data path less obvious and conflicts with the “CSV-only” intention expressed in the `data-access` spec.

**Design decisions**

- Canonical schema per dataset:
  - Define one canonical schema object per dataset (index prices, bond yields, valuations, EDB, Shibor) that captures:
    - canonical column names (English),
    - underlying CSV column names (Chinese),
    - and dtypes.
  - Use this schema in:
    - `read_csv_data` (for dtypes),
    - `add_canonical_columns` (for aliases),
    - and any data-prep functions that rely on specific columns.
  - As of this change, `data_preparation/data_fetcher.py` defines canonical schema objects for all CSV-backed tables:
    - `INDEX_PRICE_SCHEMA`, `CN_BOND_YIELD_SCHEMA`, `INDEX_VALUATION_SCHEMA`, `ECONOMIC_DATA_SCHEMA`, `SHIBOR_PRICES_SCHEMA`,
    - exposes their canonical column mappings via `CANONICAL_COL_MAPPINGS`,
    - centralizes the date-column selection logic for `CSVDataSource.fetch_table` via `DATASET_SCHEMAS`,
    - and attaches the per-table dtype mappings (`dtypes`) to each schema while still sourcing them from `config.CSV_DTYPE_MAPPING` for compatibility.
  - `read_csv_data` now prefers the `dtypes` declared on each schema (when present) and falls back to `config.CSV_DTYPE_MAPPING[table_name]` for any tables without an explicit schema.
  - `WIND_COLS` in `config.config` is retained as a legacy/index-DB helper for index-price column aliases; it mirrors the raw CSV column names already captured by `INDEX_PRICE_SCHEMA` and is not treated as a separate schema.
  - `DATA_COL_PARAM` in `config/style_config.py` continues to describe per-chart column roles (e.g., which CSV columns to use as X/Y/legend for EDB and A_IDX_VAL). These objects are consumers of the canonical CSV schemas rather than an alternative schema definition.
- CSV-only path for the app:
  - Keep `CSVDataSource` as the only data-access path used by `visualization/*`.
  - Ensure `visualization/*` does not import `data_preparation/data_access` or use SQLAlchemy sessions.
  - Treat `data_preparation/data_access.py` and `models.py` as ETL-only:
    - either move them under an ETL namespace, or
    - clearly document that they are not part of the Streamlit runtime.  
    - For this change, we take the documentation path by adding explicit module-level docstrings in `data_preparation/data_access.py` and `models.py` stating that they are ETL-only and that the Streamlit app uses the CSV-based readers instead.
- Correctness fix:
  - Fix `fetch_table` to select the correct date column based on the same canonical schema used by `read_csv_data`, rather than comparing to Enum members directly.

### 2. Chart configuration flattening

**Current state**

- `config/param_cls.py` defines:
  - low-level column params (`BaseDataColParam`, `WindIdxColParam`, `WindYieldCurveColParam`, `WindAIndexValueColParam`),
  - slider params (`DtSliderParam`, `SelectSliderParam`),
  - chart params (`BaseBarParam`, `SignalBarParam`, `IdxLineParam`, `LineParam`, `BarLineWithSignalParam`, `HeatmapParam`).
- `BarLineWithSignalParam` bundles:
  - `dt_slider_param`,
  - `bar_param`,
  - `line_param`,
  - and three flags (`isLineDrawn`, `isConvertedToPct`, `isSignalAssigned`).
- `config/style_config.py` wires many of these together into large configuration dicts plus chart params for each style framework.

**Problems**

- Chart configuration objects are carrying widget concerns (`DtSliderParam`) and behavior flags that control branching in the visualizer.
- The same chart type (bar+line+signal) can be driven by different combinations of:
  - `BarLineWithSignalParam`,
  - manual signal generation in `visualization/style.py`,
  - and specialized helpers like `draw_bar_line_chart_with_highlighted_predefined_signal`.
- Adding a new chart currently requires touching multiple files and understanding the interaction of several layers of configuration.

**Design decisions**

- Separate responsibilities:
  - **Data-prep configuration**: objects that tell data-prep helpers which columns to use and how to derive signals (e.g., which baseline windows or quantiles to compare).
  - **Chart configuration**: a minimal object that only includes axis names/types, titles, formats, and visual encoding details.
  - **Widget configuration**: slider/select-slider settings used only at the Streamlit boundary.
- Flatten chart configuration:
  - For bar+line+signal charts, introduce a single flat config struct (still Pydantic-based if useful) with:
    - axis names and types for bar and line,
    - y-axis format for each series,
    - color and stroke-dash settings.
  - In support of this, `config/param_cls.py` now defines `StyleBarLineChartConfig`, a slim Pydantic model that:
    - carries only axis names/types, title, per-series y-axis formats, colors, and stroke-dash,
    - and intentionally omits slider params and signal-behavior flags.
  - Remove `isLineDrawn`, `isConvertedToPct`, and `isSignalAssigned` flags from the core config in follow-up steps; these concerns are handled by:
    - dedicated data-prep helpers that always return the columns needed for the chart,
    - small wrapper functions for special cases (e.g., bar-only charts).

### 3. Data-prep vs rendering separation

**Current state**

- `visualization/style.py` now exposes pure data-prep helpers for all major style blocks:
  - `prepare_value_growth_data`, `prepare_index_turnover_data`, `prepare_term_spread_data`,
    `prepare_index_erp_data`, `prepare_style_focus_data`, `prepare_shibor_prices_data`,
    `prepare_housing_invest_data`.
- `generate_style_charts` calls these helpers first and then passes their outputs into the existing chart helpers (`draw_grouped_lines`, `draw_bar_line_chart_with_highlighted_signal`, `draw_bar_line_chart_with_highlighted_predefined_signal`).
- `visualization/data_visualizer.py` still has:
  - `prepare_bar_line_with_signal_data` which depends on `DtSliderParam` and mutates config objects via `isConvertedToPct`,
  - parallel paths for `draw_bar_line_chart_with_highlighted_signal`, `draw_bar_line_chart_with_highlighted_predefined_signal`, and `generate_signal`.

**Problems**

- For style charts, data-prep vs rendering is now cleanly separated, but:
  - bar+line+signal helpers still rely on behavior flags (`isLineDrawn`, `isConvertedToPct`, `isSignalAssigned`),
  - and signal computation is split between the new helpers, `np.select` blocks, and `append_signal_column`.
- For strategy-index charts, data-prep is still inline inside `visualization/stg_idx.py` (acceptable for now, but not yet using the same helper pattern).

**Design decisions**

- Keep the new style data-prep helpers as the canonical pattern going forward; do not re-introduce inline transformations in `generate_style_charts`.
- Extract a thin, shared renderer for bar+line+signal charts:
  - `draw_bar_line_chart_with_highlighted_signal` and `draw_bar_line_chart_with_highlighted_predefined_signal` both now delegate to a common `_render_bar_line_chart_with_highlighted_signal` helper that accepts an already-sliced/prepared frame and a `BarLineWithSignalParam`,
  - the renderer only builds the Altair bar/line layers and calls `st.altair_chart`, leaving date-window selection and signal computation to the caller.
- Introduce a style-specific draw helper that bridges slim configs to the existing helpers:
  - `build_bar_line_with_signal_param_for_style_chart` constructs a `BarLineWithSignalParam` from a `StyleBarLineChartConfig`, slider params, signal labels, and optional `compared_cols`,
  - `draw_style_bar_line_chart_with_highlighted_signal` uses this builder and then calls `draw_bar_line_chart_with_highlighted_signal`, ensuring style charts can migrate to slim configs without changing behavior.
- As the first adopter, the ERP style chart:
  - defines `INDEX_ERP_STYLE_CHART_CONFIG` using `StyleBarLineChartConfig`,
  - uses `draw_style_bar_line_chart_with_highlighted_signal` in `visualization/style.generate_style_charts`,
  - and is covered by additional tests that validate the end-to-end pipeline (data-prep → signal assignment → helper wiring) remains unchanged for the existing CSV snapshot.
- In a follow-up step, simplify `prepare_bar_line_with_signal_data` and the related helpers so that they:
  - no longer mutate config objects,
  - no longer depend on `DtSliderParam` for `custom_dt`,
  - and assume signals are already computed by data-prep helpers.
- Consider extracting light-weight data-prep helpers for strategy-index charts in `visualization/stg_idx.py` once style-side refactors are complete and stable.

### 4. Unified signal generation

**Current state**

- Signal mapping is now centralized:
  - `data_preparation/data_processor.apply_signal_from_conditions` implements the canonical “conditions → choices → default” mapping using `np.select`.
  - `append_signal_column` is a thin wrapper around this helper for band-style signals (target vs upper/lower bounds).
  - All style block signals (value vs growth, index turnover, credit expansion, style focus, big/small momentum, ERP and ERP_2, Shibor, and housing investment) are computed in `visualization/style.py` using `apply_signal_from_conditions`, and the corresponding chart configs set `isSignalAssigned=True`.
  - `draw_bar_line_chart_with_highlighted_signal` is the default path for bar+line+signal charts with precomputed signals (index turnover, ERP, credit expansion, Shibor, housing investment, ERP_2, style focus). `prepare_bar_line_with_signal_data` now treats any existing signal column on the input frame as authoritative and only computes signals on-the-fly (via `apply_signal_from_conditions` and `append_signal_column`) when the signal column is absent (e.g., for term-spread variants that still rely on threshold/band-based signals).
  - The legacy `generate_signal` helper in `visualization/data_visualizer.py` has been removed; `draw_bar_line_chart_with_highlighted_predefined_signal` is now only used for bar-only relative-momentum charts that do not have a line baseline.

**Problems**

- The signal API is unified, but:
  - some chart configs still carry `isSignalAssigned` flags whose behavior depends on the helper used,
  - and precomputed-signal vs on-the-fly signal generation is still split between `draw_bar_line_chart_with_highlighted_signal` and `draw_bar_line_chart_with_highlighted_predefined_signal`.

**Design decisions**

- Keep `apply_signal_from_conditions` as the single mapping primitive for signal assignment.
- Prefer precomputed signals in data-prep helpers where business logic is non-trivial (e.g., combining multiple excess-return conditions), and reserve band-style `append_signal_column` for simple threshold/band cases.
- Treat `generate_signal`-style debug helpers as dead code and remove them rather than keeping parallel paths.

### 5. Future work: signal handling and chart config

The current change intentionally stops short of fully redesigning chart configuration and signal responsibilities. Follow-up work SHOULD:

- Split configuration models so that:
  - style charts with precomputed business signals use a dedicated, minimal config that does not expose `isSignalAssigned`, `no_signal`, or band-related fields, and
  - generic bar+line+band charts retain a separate config that explicitly models threshold/band-based signal behavior.
- Split helpers so that:
  - one rendering helper assumes signals are already present on the frame and never mutates signal columns, and
  - a separate helper is responsible for purely mechanical band-based signal computation, only used by charts that opt into that behavior.
- Add guard rails and tests:
  - for style charts, assert that the expected signal column is present on the frame before rendering,
  - and add tests around style data-prep helpers to ensure they always produce the required signal columns for a fixed CSV snapshot.

### 7. Validation strategy

**Current state**

- Manual validation:
  - The style page has been repeatedly verified via `streamlit run app.py`, with side-by-side comparison of charts and signals before/after refactors.
- Automated checks:
  - `tests/test_style_prep.py` exercises:
    - `prepare_value_growth_data` to verify:
      - non-empty outputs for ratio/percentage-change/signal frames,
      - monotonic trade-date indices,
      - and that the `交易信号` column only contains the expected value/growth/neutral labels.
    - `prepare_shibor_prices_data` to verify:
      - non-empty output,
      - monotonic trade-date index,
      - and presence of the configured Shibor price and rolling-mean columns.
    - `prepare_index_turnover_data` to verify:
      - non-empty output,
      - monotonic trade-date index,
      - presence of the configured rolling-mean columns,
      - and that the `交易信号` column only contains the expected turnover signals.
    - `prepare_term_spread_data` to verify:
      - non-empty outputs for term-spread and yield-curve frames,
      - monotonic trade-date indices,
      - and presence of the configured spread and rolling-mean columns.
    - `prepare_index_erp_data` to verify:
      - non-empty ERP frame with monotonic trade-date index,
      - presence of ERP value, rolling mean, and quantile bands,
      - and that the returned ERP conditions align with the ERP frame and are boolean.
    - `prepare_big_small_momentum_data` to verify:
      - non-empty ratio/percentage-change/signal frames,
      - monotonic trade-date indices,
      - and that the `交易信号` column only contains the expected big/small signals.
    - `prepare_style_focus_data` to verify:
      - non-empty output with monotonic trade-date index,
      - presence of style-focus value and quantile columns,
      - and that the style-focus signal column only contains the expected enum values.
    - `prepare_housing_invest_data` and the inline credit-expansion prep to verify:
      - non-empty outputs with monotonic trade-date indices,
      - presence of the configured YoY and rolling-mean columns,
      - and that credit-expansion signals stay within the configured enum set.
  - `scripts/run_quick_checks.py` provides a single entry point for running the fast “style prep” test subset via `python scripts/run_quick_checks.py`, which runs `pytest -m style_prep tests`.

**Planned extensions**

- Incrementally extend automated coverage to:
  - index turnover (`prepare_index_turnover_data`),
  - term spread (`prepare_term_spread_data`),
  - ERP / ERP_2 (`prepare_index_erp_data`),
  - credit expansion, style focus, and housing investment.
- For each helper, assert a minimal set of invariants:
  - monotonic date index,
  - presence of expected canonical columns and signal columns,
  - and that signal values remain within the configured enum set.
- Recommend wiring `scripts/run_quick_checks.py` into a Git pre-commit hook, for example:
  - `.git/hooks/pre-commit`:
    - `#!/usr/bin/env bash`
    - `python scripts/run_quick_checks.py || exit 1`

### 6. Dead code removal

**Current state**

- As of this change, `config/style_config.py` and `visualization/style.py` no longer contain large commented-out legacy chart helpers or alternate ERP conditions.
- Domain-level NOTE comments are retained to document style frameworks and business intent, but debug-only `st.write` calls and the old `draw_test` path have been removed.

**Problems**

- Previously, commented-out code hid the real behavior and encouraged “just in case” branches instead of clean abstractions.

**Design decisions**

- Systematically remove:
  - unused chart helpers,
  - large commented-out sections,
  - and debug-only `st.write` calls.
- Keep only:
  - high-signal comments documenting domain formulas or business rules,
  - and TODOs with clear, actionable next steps.
