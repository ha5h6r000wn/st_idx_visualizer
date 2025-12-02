# Change: Refactor data layer to CSV-only and clean chart prep/render

## Why
- Data source selection is scattered across branches, duplicating filters and producing inconsistent schemas between CSV and legacy database paths.
- The legacy database path adds complexity but is unused in practice; it also carries a hard-coded connection string risk.
- Mixed Chinese/English column names force table-specific conditionals and brittle filtering.
- Chart helpers bundle data prep, signal generation, and rendering, while commented-out code remains in place.

## What Changes
- Collapse to a single CSV-backed `DataSource` implementation with dataset metadata for filters and column mappings so consumers call a single fetch API without branching.
- Normalize returned DataFrames to canonical schemas per dataset and keep aliasing for existing Chinese labels to avoid breaking charts.
- Remove the unused database session code and configuration switches that only add dead branches.
- Split `draw_bar_line_chart_with_highlighted_signal` into pure data prep + rendering, trim dead/commented blocks, and simplify parameter objects to the minimal fields in use.

## Impact
- Affected specs: data-access, visualization
- Affected code: data_preparation/data_fetcher.py, data_preparation/db.py (deleted), config/config.py, config/style_config.py, visualization/data_visualizer.py
- No code changes until this proposal is approved.
