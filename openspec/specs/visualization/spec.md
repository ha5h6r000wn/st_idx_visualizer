# visualization Specification

## Purpose
TBD - created by archiving change refactor-data-layer. Update Purpose after archive.
## Requirements
### Requirement: Separated chart data preparation
The system SHALL provide pure data-preparation functions for bar+line-with-signal and style framework charts that produce the frames needed for rendering, independent of Streamlit state and widget interactions.

#### Scenario: Prepare once, render multiple
- **WHEN** chart data is prepared for a slider-selected window or style block (e.g., value vs growth, term spread, ERP, style focus)
- **THEN** the resulting DataFrame can be passed to the rendering helper without recomputing signals or re-parsing slider inputs, and can be reused across multiple charts or contexts.

#### Scenario: Reuse outside Streamlit
- **WHEN** a prep function is invoked from a test or CLI context
- **THEN** it returns the same structure as the Streamlit path, enabling validation without UI dependencies.

### Requirement: Minimal chart configuration surface
The system SHALL reduce chart helpers to accept only the fields actually used for encoding (axis names/types, number formatting, colors, stroke dash, legend placement) and avoid nested Pydantic wrappers or behavior flags when a flat configuration suffices.

#### Scenario: Add new style chart variant
- **WHEN** a new style chart variant (e.g., another macro signal) is added
- **THEN** it can be configured by passing a flat config object that does not embed widget configuration or behavioral flags (such as `isLineDrawn`, `isConvertedToPct`, `isSignalAssigned`), and no nested models are required when a single object suffices.

### Requirement: Remove dead chart code
The repository SHALL not contain large commented-out chart helper implementations or unused visualization code paths.

#### Scenario: Legacy test helper and debug remnants
- **WHEN** the previous `draw_test` helper, duplicate bar+line+signal rendering paths, or large commented blocks are unused
- **THEN** they are removed rather than left as commented blocks, keeping only minimal domain-explanatory comments.

