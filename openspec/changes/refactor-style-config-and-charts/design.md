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
- CSV-only path for the app:
  - Keep `CSVDataSource` as the only data-access path used by `visualization/*`.
  - Ensure `visualization/*` does not import `data_preparation/data_access` or use SQLAlchemy sessions.
  - Treat `data_preparation/data_access.py` and `models.py` as ETL-only; either move them under an ETL namespace or clearly document that they are not part of the Streamlit runtime.
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
    - color and stroke-dash settings,
    - and legend placement.
  - Remove `isLineDrawn`, `isConvertedToPct`, and `isSignalAssigned` flags from the core config; these concerns are handled by:
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
- In a follow-up step, simplify `prepare_bar_line_with_signal_data` and the related helpers so that they:
  - no longer mutate config objects,
  - no longer depend on `DtSliderParam` for `custom_dt`,
  - and assume signals are already computed by data-prep helpers.
- Consider extracting light-weight data-prep helpers for strategy-index charts in `visualization/stg_idx.py` once style-side refactors are complete and stable.

### 4. Unified signal generation

**Current state**

- Signal semantics are implemented in multiple places:
  - manual `np.select` blocks in `visualization/style.py`,
  - `append_signal_column` and `assign_signal` in `data_preparation/data_processor.py`,
  - conditional logic in `prepare_bar_line_with_signal_data` and `generate_signal`.

**Problems**

- This duplication invites subtle differences in behavior if one path is updated and others are not.
- Some helpers (`generate_signal`) mix computation with Streamlit logging (`st.write`), which is undesirable for core logic.

**Design decisions**

- Define one canonical signal API:
  - A single helper, e.g., `compute_band_signal(frame, target, upper, lower, labels)`, that:
    - uses clear, explicit column names,
    - returns the input frame with a new signal column.
  - This helper can be a thin wrapper around the existing `append_signal_column` but without Streamlit dependencies.
- Bar+line+signal charts:
  - All such charts compute signals via this API, whether they are quantile-based, mean-based, or band-based.
  - Specialized conditions (e.g., combining two period excess returns) remain in the style data-prep helpers, but the final mapping from thresholds to labels uses the shared signal function.

### 5. Dead code removal

**Current state**

- `config/style_config.py` and `visualization/style.py` contain large commented blocks and legacy code paths (e.g., old `draw_test` helper usage and alternative ERP conditions).

**Problems**

- Commented-out code hides the real behavior and encourages “just in case” branches instead of clean abstractions.

**Design decisions**

- Systematically remove:
  - unused chart helpers,
  - large commented-out sections,
  - and debug-only `st.write` calls.
- Keep only:
  - high-signal comments documenting domain formulas or business rules,
  - and TODOs with clear, actionable next steps.
