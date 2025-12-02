## ADDED Requirements
### Requirement: Separated chart data preparation
The system SHALL provide a pure data-preparation function for bar+line-with-signal charts that produces the frame needed for rendering, independent of Streamlit state.

#### Scenario: Prepare once, render multiple
- **WHEN** chart data is prepared for a slider-selected window
- **THEN** the resulting DataFrame can be passed to the rendering helper without recomputing signals or re-parsing slider inputs.

#### Scenario: Reuse outside Streamlit
- **WHEN** the prep function is invoked from a test or CLI context
- **THEN** it returns the same structure as the Streamlit path, enabling validation without UI dependencies.

### Requirement: Minimal chart configuration surface
The system SHALL reduce the bar+line+signal chart helper to accept only the fields actually used for encoding (axis names/types, number formatting, colors, stroke dash) and avoid nested Pydantic wrappers when a flat config suffices.

#### Scenario: Add new chart variant
- **WHEN** a new chart variant is added
- **THEN** it can be configured by passing a flat config object without duplicating nested models or extra flags.

### Requirement: Remove dead chart code
The repository SHALL not contain large commented-out chart helper implementations.

#### Scenario: Legacy test helper
- **WHEN** the previous `draw_test` helper is unused
- **THEN** it is removed rather than left as a commented block.
