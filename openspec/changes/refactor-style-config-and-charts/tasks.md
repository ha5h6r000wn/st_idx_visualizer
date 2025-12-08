## Tasks

- [ ] Inventory current style and strategy-index chart paths
  - [ ] Map each chart in `visualization/stg_idx.py` and `visualization/style.py` to:
    - data sources (CSV tables),
    - transformation helpers,
    - and chart helpers.
  - [ ] Document which configurations in `config/style_config.py` and `config/param_cls.py` are used by each chart.

- [ ] Refine data-access behavior for CSV-only paths
  - [x] Fix the `CSVDataSource.fetch_table` date-column selection bug for `A_IDX_PRICE` while keeping behavior for other tables unchanged.
  - [x] Confirm that `Streamlit` UI modules (`visualization/*.py`) do not rely on `data_preparation/data_access.py` or database sessions.
  - [x] If `data_preparation/data_access.py` is unused by the app, either:
    - [ ] Move it under an ETL-specific namespace, or
    - [x] Clearly document in `data_preparation/data_access.py` and `models.py` that they are ETL-only and not part of the Streamlit runtime, or
    - [ ] Remove it in a separate, clearly documented step consistent with the `data-access` spec.

- [ ] Simplify and clarify chart configuration models
  - [ ] Audit `config/param_cls.py` usage to identify:
    - unused or redundant fields and models,
    - boolean flags (`isLineDrawn`, `isConvertedToPct`, `isSignalAssigned`) that drive complex branching in the visualizer.
  - [ ] Introduce a flatter chart configuration for bar+line+signal charts that:
    - [ ] keeps only axis names/types, formats, stroke dash, and color (initial scaffolding via `StyleBarLineChartConfig` complete; ERP chart is wired through this path),
    - [ ] decouples slider configuration from chart configuration,
    - [ ] and maintains Pydantic usage only where it adds validation value.
  - [ ] Update `config/style_config.py` to use the flatter configuration for existing style charts without changing behavior.

- [ ] Separate data preparation from rendering for style charts
  - [ ] Extract pure data-preparation helpers for each major style component:
    - [x] 价值成长比价与相对动量
    - [x] 市场情绪（换手率）
    - [x] 期限利差与期现利差
    - [x] ERP 股债性价比
    - [x] 风格关注度
    - [x] 货币周期（Shibor）
    - [x] 经济增长（地产投资）
    - [x] 大盘/小盘相对动量
  - [x] Ensure these helpers:
    - [x] accept well-typed inputs (canonical DataFrames and parameter objects),
    - [x] return fully prepared frames ready for charting,
    - [x] avoid direct Streamlit calls or widget interactions.
  - [x] Adapt `visualization/style.py` to:
    - [x] call data-prep helpers first,
    - [x] then pass their outputs into existing `data_visualizer` chart helpers.

- [x] Unify and de-duplicate signal generation logic
  - [x] Consolidate `np.select`-based signal logic in `visualization/style.py` and `append_signal_column` in `data_preparation/data_processor.py` into a single, reusable pattern.
  - [x] Update bar+line+signal charts to use the unified signal-generator, keeping current signal semantics intact.
  - [x] Remove or simplify the separate `generate_signal` and `draw_bar_line_chart_with_highlighted_predefined_signal` paths if they become redundant after unification.

- [ ] Consolidate dataset schema definitions
  - [x] Review `CANONICAL_COL_MAPPINGS`, `CSV_DTYPE_MAPPING`, `WIND_COLS`, and `DATA_COL_PARAM` for overlapping responsibilities.
  - [ ] Define a single source of truth per dataset for:
    - canonical column names,
    - CSV column dtypes,
    - and any required aliases for charts.
  - [ ] Update consumers in `data_preparation` and `visualization` to use these canonical definitions, keeping all existing Chinese labels.
    - [x] Style-path consumers for EDB (via `DATA_COL_PARAM[param_cls.WindPortal.EDB]`) now reference the canonical CSV column names directly instead of SQL parser aliases.
    - [x] Style-path consumers for CN_BOND_YIELD (via `YIELD_CURVE_COL_PARAM`) are wired to the canonical CSV column names while preserving Chinese labels used in charts.

- [x] Remove dead or commented-out chart code
  - [x] Identify large commented blocks in `config/style_config.py` and `visualization/style.py` that are no longer relevant.
  - [x] Remove legacy chart helpers or comments (e.g., old `draw_test` paths) in line with the `visualization` spec’s “Remove dead chart code” requirement.
  - [x] Keep small, high-signal comments where they clarify domain-specific behavior.

- [ ] Validation
  - [x] Add minimal tests or scripts that:
    - [x] exercise data-prep functions for key style components with fixture CSVs under `data/` (value-vs-growth, Shibor, index turnover, term spread, ERP/ERP_2, credit expansion, style focus, housing investment, big-small momentum),
    - [x] assert key invariants (e.g., presence of canonical columns, monotonic date indices, and signal values within the configured enum sets),
    - [x] cover `prepare_bar_line_with_signal_data` and `DtSliderParam`-driven window selection to ensure chart helpers respect precomputed signals and slider defaults.
    - [x] validate that `fetch_data_from_local` respects the canonical dataset schemas for `CN_BOND_YIELD`, `A_IDX_VAL`, `EDB`, and `SHIBOR_PRICES` via `tests/test_data_fetcher_schema.py`.
    - [x] add invariants for the strategy-index page via `tests/test_stg_idx_prep.py`, asserting:
      - non-empty grouped-return frames that cover all configured strategy indices by name,
      - NAV wide frames with monotonic date indices and non-empty series for each index,
      - and symmetric excess-return correlation matrices with unit diagonal for the stg_idx heatmap.
  - [ ] Manually run `streamlit run app.py` and verify:
    - [x] all charts render without errors,
    - [x] chart values and signals visually match pre-change behavior for a fixed snapshot of CSV data.
