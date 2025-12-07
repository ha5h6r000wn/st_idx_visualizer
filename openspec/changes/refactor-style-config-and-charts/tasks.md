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
    - [ ] keeps only axis names/types, formats, stroke dash, and color,
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

- [x] Remove dead or commented-out chart code
  - [x] Identify large commented blocks in `config/style_config.py` and `visualization/style.py` that are no longer relevant.
  - [x] Remove legacy chart helpers or comments (e.g., old `draw_test` paths) in line with the `visualization` spec’s “Remove dead chart code” requirement.
  - [x] Keep small, high-signal comments where they clarify domain-specific behavior.

- [ ] Validation
  - [ ] Add minimal tests or scripts that:
    - [x] exercise data-prep functions for key style components with fixture CSVs under `data/` (starting with value-vs-growth, Shibor, index turnover, and term spread),
    - [ ] extend coverage to remaining style components (ERP/ERP_2, credit expansion, style focus, housing investment),
    - [ ] and assert key invariants (e.g., presence of canonical columns, monotonic date indices).
  - [ ] Manually run `streamlit run app.py` and verify:
    - [ ] all charts render without errors,
    - [ ] chart values and signals visually match pre-change behavior for a fixed snapshot of CSV data.
