## Summary

Refactor the style- and strategy-index visualization paths to simplify configuration, remove dead code, and make data preparation independent from Streamlit widgets while preserving all existing chart behavior and labels.

## Motivation

- The `config/style_config.py` and `visualization/style.py` modules have grown into large, tightly coupled blobs that mix:
  - data-fetch/query configuration,
  - chart configuration (axis labels, titles, formats),
  - and business logic for signal generation and macro-style frameworks.
- Chart configuration is expressed through deeply nested Pydantic models (`BarLineWithSignalParam`, `SignalBarParam`, `LineParam`, `DtSliderParam`) and boolean flags (`isLineDrawn`, `isConvertedToPct`, `isSignalAssigned`) that drive multiple code paths in `visualization/data_visualizer.py`.
- The bar+line+signal path has overlapping helpers:
  - `prepare_bar_line_with_signal_data`
  - `draw_bar_line_chart_with_highlighted_signal`
  - `draw_bar_line_chart_with_highlighted_predefined_signal`
  - ad-hoc `np.select`-based logic in `visualization/style.py`
  creating multiple ways to compute essentially the same signals.
- The data layer now uses CSV-only access via `CSVDataSource`, but:
  - `data_preparation/data_access.py` and `models.py` still describe database paths,
  - there is a small bug in `CSVDataSource.fetch_table` (date column selection for `A_IDX_PRICE`),
  - and we still carry multiple overlapping definitions of dataset schemas (`CANONICAL_COL_MAPPINGS`, `CSV_DTYPE_MAPPING`, `WIND_COLS`, and `DATA_COL_PARAM`).

This complexity makes it harder to:

- add or modify style frameworks (e.g., another relative momentum or macro indicator),
- reason about where a particular chart’s behavior is defined,
- and validate behavior without going through Streamlit.

We already have `data-access` and `visualization` specs that push in the direction of:

- CSV-only data paths with normalized schemas, and
- separated data-preparation vs rendering helpers with a minimal configuration surface.

This change aligns implementation with those specs while keeping the UI behavior stable.

## Non-goals

- No change to chart semantics, labels, or default slider ranges as seen in the Streamlit UI.
- No introduction of a new database backend or additional data sources.
- No replacement of Streamlit/Altair; only internal structure and helpers are touched.

## Scope

- **Visualization & style framework**
  - `visualization/style.py`
  - `visualization/data_visualizer.py`
  - `config/param_cls.py`
  - `config/style_config.py`
- **Data access**
  - `data_preparation/data_fetcher.py`
  - `data_preparation/data_access.py` (only to clarify/remove unused session-based paths as needed)
  - `models.py` (only if required to satisfy data-access specs; otherwise left as ETL-only)

## Risks and Constraints

- **Never break userspace**
  - The current Streamlit dashboard (tabs, charts, labels, default windows) is the “userspace” here; any behavioral change in chart values, signals, or slider defaults is a regression.
- **Spec alignment**
  - Changes must remain consistent with existing `data-access` and `visualization` specs, or extend them via explicit deltas.
- **Incremental refactor**
  - The style module is large; refactors must land as small, verifiable steps with clear data-prep helpers and tests where feasible.

## Acceptance Criteria

- Chart outputs (values, signals, labels) for existing tabs:
  - 策略指数页面 (`visualization/stg_idx.py`)
  - 风格研判页面 (`visualization/style.py`)
  remain identical for the same input CSVs.
- The bar+line+signal path has:
  - a single, spec-compliant data-preparation helper that can run without Streamlit,
  - a thin rendering helper whose configuration is limited to axis names/types, formats, and colors.
- There is a clear, single source of truth for each dataset’s canonical schema.
- Unused database session paths are either:
  - removed from the runtime code paths used by Streamlit, or
  - explicitly isolated as ETL-only, with the CSV-backed `DataSource` remaining the only path for the app.

